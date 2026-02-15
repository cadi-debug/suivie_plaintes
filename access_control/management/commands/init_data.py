# access_control/management/commands/init_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from access_control.models import User, Institution
from dossiers.models import Plainte
from workflow.models import EtapeProcessus

class Command(BaseCommand):
    help = 'Initialise la base de données avec des utilisateurs et des dossiers de test'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- Début de l'initialisation ---")

        # 1. Création des Institutions
        tgi, _ = Institution.objects.get_or_create(
            nom="TGI de Kinshasa/Gombe",
            defaults={'type_inst': 'TRIBUNAL_GRANDE_INSTANCE', 'ville': 'Kinshasa'}
        )
        mairie, _ = Institution.objects.get_or_create(
            nom="Hôtel de Ville",
            defaults={'type_inst': 'MAIRIE', 'ville': 'Kinshasa'}
        )
        
        self.stdout.write(self.style.SUCCESS(f"Institutions créées : {tgi}, {mairie}"))

        # 2. Création des Utilisateurs (Mot de passe pour tous : 'pass1234')
        users_data = [
            {'username': 'admin', 'role': 'ADMIN_SYS', 'inst': None, 'is_staff': True},
            {'username': 'greffier', 'role': 'GREFFIER', 'inst': tgi, 'is_staff': False},
            {'username': 'procureur', 'role': 'PROCUREUR', 'inst': tgi, 'is_staff': False},
            {'username': 'juge', 'role': 'JUGE', 'inst': tgi, 'is_staff': False},
            {'username': 'agent_mairie', 'role': 'ADMIN_MAIRIE', 'inst': mairie, 'is_staff': False},
        ]

        for u in users_data:
            user, created = User.objects.get_or_create(username=u['username'])
            user.set_password('pass1234') # Important pour hasher le MDP
            user.role = u['role']
            user.institution = u['inst']
            user.is_staff = u['is_staff']
            if u['is_staff']: user.is_superuser = True
            user.save()
        
        self.stdout.write(self.style.SUCCESS("Utilisateurs créés (MDP: pass1234)"))

        # 3. Création d'un Dossier de Test (Pour voir le graphe tout de suite)
        greffier = User.objects.get(username='greffier')
        
        dossier, created = Plainte.objects.get_or_create(
            objet="Litige Foncier Parcelle 12B",
            defaults={
                'plaignant_nom': 'Jean Kabuya',
                'plaignant_contact': '+243 81 000 0000',
                'categorie': 'CIVIL',
                'description': 'Conflit de bornage avec le voisin Mr. Mputu.'
            }
        )

        if created:
            # Création de l'historique (Le Graphe)
            # Étape 1 : Dépôt
            etape1 = EtapeProcessus.objects.create(
                plainte=dossier,
                type_etape='DEPOT',
                auteur=greffier,
                commentaire_interne="Dossier complet, frais payés.",
                message_public="Votre dossier a été enregistré au greffe.",
                date_traitement=timezone.now() - timezone.timedelta(days=5)
            )

            # Étape 2 : Recevabilité (Le lendemain)
            procureur = User.objects.get(username='procureur')
            etape2 = EtapeProcessus.objects.create(
                plainte=dossier,
                type_etape='RECEVABILITE',
                auteur=procureur,
                commentaire_interne="Dossier recevable, transmis pour instruction.",
                message_public="Dossier jugé recevable.",
                etape_precedente=etape1, # LIEN DU GRAPHE
                date_traitement=timezone.now() - timezone.timedelta(days=4)
            )
            
            # Étape 3 : Audience (Aujourd'hui)
            etape3 = EtapeProcessus.objects.create(
                plainte=dossier,
                type_etape='AUDIENCE',
                auteur=greffier,
                commentaire_interne="Convocations envoyées.",
                message_public="Audience fixée au 15 du mois prochain.",
                etape_precedente=etape2, # LIEN DU GRAPHE
                date_traitement=timezone.now()
            )

            self.stdout.write(self.style.SUCCESS(f"Dossier de test créé : {dossier.uuid_public}"))
        
        self.stdout.write(self.style.SUCCESS("--- Initialisation Terminée ---"))