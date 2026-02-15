# workflow/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from dossiers.models import Plainte
from .models import EtapeProcessus

def home(request):
    """Page d'accueil avec recherche"""
    if request.method == 'POST':
        uuid_saisi = request.POST.get('dossier_id', '').strip()
        plainte = Plainte.objects.filter(uuid_public__icontains=uuid_saisi).first()
        
        if plainte:
            return redirect('suivi_public', uuid=plainte.uuid_public)
        else:
            messages.error(request, "Référence introuvable. Veuillez vérifier votre code.")
            
    return render(request, 'workflow/home.html')

def graph_data(request, uuid):
    """
    API D3.js : Renvoie TOUS les nœuds (passés et futurs)
    """
    plainte = get_object_or_404(Plainte, uuid_public=uuid)
    
    # Récupérer l'historique réel en dictionnaire pour accès rapide par type
    historique_reel = {e.type_etape: e for e in plainte.historique.all()}
    
    # Définition du chemin standard (Linéaire)
    roadmap = [
        ('DEPOT', 'Dépôt de la plainte'),
        ('RECEVABILITE', 'Examen de recevabilité'),
        ('ENQUETE', 'Enquête / Instruction'),
        ('AUDIENCE', 'Audience fixée'),
        ('DELIBERE', 'Mise en délibéré'),
        ('JUGEMENT', 'Jugement rendu'),
    ]
    
    # Définition des fins possibles (Branching)
    end_states = [
        ('CLOTURE', 'Dossier archivé'),
        ('REJET', 'Dossier rejeté')
    ]

    nodes = []
    links = []
    
    # --- 1. CONSTRUCTION DES NOEUDS ---
    
    # A. Le parcours linéaire
    last_real_step_index = -1
    
    # On détermine où on est dans le processus
    for i, (code, label) in enumerate(roadmap):
        step_data = historique_reel.get(code)
        
        node = {
            "id": code, # On utilise le CODE comme ID pour simplifier le lien
            "label": label,
            "type_code": code,
            "status": "future", # Par défaut
            "date_str": "À venir",
            "timestamp": 0,
            "auteur": "-",
            "message": "",
            "document_url": None
        }

        if step_data:
            node["status"] = "completed"
            node["date_str"] = step_data.date_traitement.strftime("%d/%m/%Y")
            node["timestamp"] = int(step_data.date_traitement.timestamp())
            node["auteur"] = f"{step_data.auteur.username}"
            node["message"] = step_data.message_public
            if step_data.document_joint:
                node["document_url"] = step_data.document_joint.url
            
            # Si c'est la dernière étape RÉELLE et que le dossier n'est pas clos
            # Note: Si le dossier est clos, le statut restera "completed"
            last_real_step_index = i

        nodes.append(node)

    # B. Les fins possibles (Branching)
    is_closed_or_rejected = plainte.est_cloture
    
    for code, label in end_states:
        step_data = historique_reel.get(code)
        
        node = {
            "id": code,
            "label": label,
            "type_code": code,
            "status": "future",
            "date_str": "-",
            "timestamp": 0,
            "auteur": "-",
            "message": "",
            "document_url": None
        }
        
        if step_data:
            node["status"] = "completed" # Ou "current" si on veut
            node["date_str"] = step_data.date_traitement.strftime("%d/%m/%Y")
            node["timestamp"] = int(step_data.date_traitement.timestamp())
            node["auteur"] = f"{step_data.auteur.username}"
            node["message"] = step_data.message_public
            if step_data.document_joint:
                node["document_url"] = step_data.document_joint.url
        
        # Logique visuelle : Si le dossier est fini mais pas par ce chemin là
        # Ex: Fini par REJET, donc CLOTURE est "skipped" (ou reste future/grisé)
        if is_closed_or_rejected and not step_data:
            node["status"] = "skipped" # Pourra être grisé plus fortement

        nodes.append(node)

    # Gestion du statut "current" (Le dernier nœud atteint)
    # On cherche le nœud le plus récent dans l'historique réel
    if plainte.historique.exists():
        last_step_obj = plainte.historique.last()
        for node in nodes:
            if node["id"] == last_step_obj.type_etape:
                if not plainte.est_cloture:
                     node["status"] = "current"
                else:
                     node["status"] = "completed" # Reste vert si fini
                break

    # --- 2. CONSTRUCTION DES LIENS (LOGIQUE FIXE) ---
    
    # Liens linéaires (0 -> 1 -> 2 -> 3 -> 4 -> 5)
    for i in range(len(roadmap) - 1):
        links.append({
            "source": roadmap[i][0],
            "target": roadmap[i+1][0]
        })
        
    # Liens de bifurcation (JUGEMENT -> CLOTURE et JUGEMENT -> REJET)
    last_linear_id = roadmap[-1][0] # JUGEMENT
    for code, _ in end_states:
        links.append({
            "source": last_linear_id,
            "target": code
        })
            
    return JsonResponse({"nodes": nodes, "links": links})

def suivi_public(request, uuid):
    plainte = get_object_or_404(Plainte, uuid_public=uuid)
    return render(request, 'workflow/suivi_public.html', {'plainte': plainte})