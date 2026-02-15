# dossiers/models.py
from django.db import models
import uuid

class Plainte(models.Model):
    CATEGORIES = [
        ('PENAL', 'Affaire Pénale (Vol, Agression...)'),
        ('CIVIL', 'Affaire Civile (Divorce, Foncier...)'),
        ('ADMIN', 'Administratif (État civil, Urbanisme)'),
    ]
    
    uuid_public = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    plaignant_nom = models.CharField(max_length=255)
    plaignant_contact = models.CharField(max_length=100, help_text="Email ou Téléphone")
    
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    objet = models.CharField(max_length=255)
    description = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    est_cloture = models.BooleanField(default=False)

    def __str__(self):
        return f"Dossier #{str(self.uuid_public)[:8]} - {self.objet}"

class PieceConviction(models.Model):
    TYPES_PIECE = [
        ('NUMERIQUE', 'Fichier Numérique (PDF, Image, Audio)'),
        ('PHYSIQUE', 'Objet Physique / Matériel (Scellé)'),
    ]
    
    plainte = models.ForeignKey(Plainte, on_delete=models.CASCADE, related_name='pieces')
    nom = models.CharField(max_length=255, verbose_name="Nom de la pièce")
    description = models.TextField(blank=True, verbose_name="Description détaillée")
    type_piece = models.CharField(max_length=20, choices=TYPES_PIECE, default='NUMERIQUE')
    
    # Null=True et Blank=True car facultatif pour les objets physiques
    fichier = models.FileField(upload_to='preuves/%Y/%m/', null=True, blank=True)
    
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nom} ({self.get_type_piece_display()})"