# access_control/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class Institution(models.Model):
    TYPES = [
        ('TRIBUNAL_PAIX', 'Tribunal de Paix'),
        ('TRIBUNAL_GRANDE_INSTANCE', 'Tribunal de Grande Instance'),
        ('PARQUET', 'Parquet / Procureur'),
        ('MAIRIE', 'Mairie / Commune'),
        ('COMMISSARIAT', 'Commissariat de Police'),
    ]
    nom = models.CharField(max_length=255)
    type_inst = models.CharField(max_length=50, choices=TYPES)
    ville = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nom} ({self.get_type_inst_display()})"

class User(AbstractUser):
    ROLES = [
        ('GREFFIER', 'Greffier (Réception & Saisie)'),
        ('OPJ', 'Officier Police Judiciaire'),
        ('PROCUREUR', 'Procureur (Instruction)'),
        ('JUGE', 'Juge (Décision)'),
        ('ADMIN_MAIRIE', 'Agent Administratif Mairie'),
        ('ADMIN_SYS', 'Administrateur Système'),
    ]
    role = models.CharField(max_length=20, choices=ROLES, default='GREFFIER')
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Pour savoir qui a traité le dossier
    def __str__(self):
        return f"{self.last_name} {self.first_name} - {self.get_role_display()}"

