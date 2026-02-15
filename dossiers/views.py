# dossiers/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from .models import Plainte
from .forms import PieceConvictionForm, PlainteForm, EtapeForm, PieceFormSet, PieceConvictionForm
from workflow.models import EtapeProcessus
import qrcode
import base64
from io import BytesIO


@login_required
def dashboard(request):
    # Récupération initiale de toutes les plaintes (du plus récent au plus vieux)
    plaintes = Plainte.objects.all().order_by('-date_creation')
    
    # Gestion de la recherche HTMX
    query = request.GET.get('search', '')
    if query:
        plaintes = plaintes.filter(
            Q(objet__icontains=query) | 
            Q(plaignant_nom__icontains=query) |
            Q(uuid_public__icontains=query)
        )
    
    # Si la requête vient de HTMX, on renvoie seulement les lignes du tableau
    if request.headers.get('HX-Request'):
        return render(request, 'dossiers/partials/plainte_list.html', {'plaintes': plaintes})
    
    # Sinon, on renvoie la page complète
    return render(request, 'dossiers/dashboard.html', {'plaintes': plaintes})


@login_required
@transaction.atomic
def plainte_create(request):
    if request.method == 'POST':
        form = PlainteForm(request.POST)
        formset = PieceFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            # 1. On sauvegarde la plainte d'abord pour avoir un ID
            plainte = form.save()
            
            # 2. On récupère les pièces sans les sauvegarder en base (commit=False)
            pieces = formset.save(commit=False)
            
            # 3. CORRECTION ICI : On assigne la plainte manuellement et on sauvegarde
            for piece in pieces:
                piece.plainte = plainte  # On lie la pièce à la plainte créée
                piece.save()             # On sauvegarde la pièce maintenant qu'elle a un parent
            
            # 4. Création de l'étape initiale (inchangé)
            EtapeProcessus.objects.create(
                plainte=plainte,
                type_etape='DEPOT',
                auteur=request.user,
                message_public="Dossier créé."
            )
            return redirect('plainte_detail', uuid=plainte.uuid_public)
    else:
        form = PlainteForm()
        formset = PieceFormSet()
        
    return render(request, 'dossiers/plainte_create.html', {
        'form': form, 
        'formset': formset
    })


@login_required
def plainte_detail(request, uuid):
    plainte = get_object_or_404(Plainte, uuid_public=uuid)
    historique = plainte.historique.all().order_by('-date_traitement')
    
    # Formulaire Workflow
    form_etape = EtapeForm(plainte=plainte)
    # Formulaire Ajout Pièce (indépendant)
    form_piece = PieceConvictionForm()

    if request.method == 'POST':
        # CAS 1 : Ajout d'une pièce depuis le détail
        if 'submit_piece' in request.POST:
            form_piece = PieceConvictionForm(request.POST, request.FILES)
            if form_piece.is_valid():
                piece = form_piece.save(commit=False)
                piece.plainte = plainte
                piece.save()
                return redirect('plainte_detail', uuid=plainte.uuid_public)
        
        # CAS 2 : Changement d'étape
        elif 'submit_etape' in request.POST:
            form_etape = EtapeForm(request.POST, request.FILES, plainte=plainte)
            if form_etape.is_valid():
                etape = form_etape.save(commit=False)
                etape.plainte = plainte
                etape.auteur = request.user
                etape.etape_precedente = historique.first()
                etape.save()
                
                if etape.type_etape in ['CLOTURE', 'REJET']:
                    plainte.est_cloture = True
                    plainte.save()
                return redirect('plainte_detail', uuid=plainte.uuid_public)

    return render(request, 'dossiers/plainte_detail.html', {
        'plainte': plainte,
        'historique': historique,
        'form': form_etape,
        'piece_form': form_piece
    })



def generer_recepisse(request, uuid):
    plainte = get_object_or_404(Plainte, uuid_public=uuid)
    
    # 1. Générer le QR Code en mémoire
    url_suivi = request.build_absolute_uri(f'/suivi/{plainte.uuid_public}/')
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url_suivi)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    # 2. Convertir en base64 pour l'afficher dans le HTML sans sauvegarder l'image
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'plainte': plainte,
        'qr_code': qr_image_base64,
        'agent': request.user
    }
    return render(request, 'dossiers/recepisse_print.html', context)


# dossiers/views.py (Ajout)
@login_required
def ajouter_piece(request, uuid):
    plainte = get_object_or_404(Plainte, uuid_public=uuid)
    if request.method == 'POST':
        form = PieceConvictionForm(request.POST, request.FILES) # IMPORTANT: request.FILES
        if form.is_valid():
            piece = form.save(commit=False)
            piece.plainte = plainte
            piece.save()
            return redirect('plainte_detail', uuid=plainte.uuid_public)
    return redirect('plainte_detail', uuid=plainte.uuid_public)
