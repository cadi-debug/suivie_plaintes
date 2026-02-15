# workflow/models.py
from django.db import models
from django.conf import settings
from dossiers.models import Plainte # Assurez-vous que l'import est correct selon votre structure

class EtapeProcessus(models.Model):
    TYPES_ETAPE = [
        ('DEPOT', 'Dépôt de la plainte'),
        ('RECEVABILITE', 'Examen de recevabilité'),
        ('ENQUETE', 'Enquête / Instruction en cours'),
        ('AUDIENCE', 'Audience fixée'),
        ('DELIBERE', 'Mise en délibéré'),
        ('JUGEMENT', 'Jugement rendu / Résolution'),
        ('CLOTURE', 'Dossier archivé'),
        ('REJET', 'Dossier rejeté / Classé sans suite'),
    ]
    
    plainte = models.ForeignKey(Plainte, on_delete=models.CASCADE, related_name='historique')
    type_etape = models.CharField(max_length=50, choices=TYPES_ETAPE)
    
    # Qui a fait cette action ? (Traçabilité)
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    date_traitement = models.DateTimeField(auto_now_add=True)
    commentaire_interne = models.TextField(blank=True, help_text="Visible seulement par les employés")
    message_public = models.TextField(blank=True, help_text="Ce qui apparaitra sur le graphe du citoyen")
    
    # Pour le graphe : permet de lier cette étape à la précédente
    etape_precedente = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    
    document_joint = models.FileField(
        upload_to='procedure_actes/%Y/%m/', 
        null=True, 
        blank=True, 
        verbose_name="Acte / Jugement / Notification (PDF/Image)"
    )

    class Meta:
        ordering = ['date_traitement']

    def __str__(self):
        return f"{self.get_type_etape_display()} par {self.auteur}"