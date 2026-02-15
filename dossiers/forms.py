# dossiers/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Plainte, PieceConviction
from workflow.models import EtapeProcessus

class PlainteForm(forms.ModelForm):
    class Meta:
        model = Plainte
        fields = ['plaignant_nom', 'plaignant_contact', 'categorie', 'objet', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class PieceConvictionForm(forms.ModelForm):
    class Meta:
        model = PieceConviction
        fields = ['nom', 'type_piece', 'description', 'fichier']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'w-full border p-2 rounded', 'placeholder': 'Nom (ex: Arme, Photo...)'}),
            'type_piece': forms.Select(attrs={'class': 'w-full border p-2 rounded'}),
            'description': forms.Textarea(attrs={'rows': 1, 'class': 'w-full border p-2 rounded', 'placeholder': 'Description courte...'}),
            'fichier': forms.FileInput(attrs={'class': 'w-full text-xs'}),
        }

# Configuration du FormSet : extra=1 affiche une ligne vide par défaut
PieceFormSet = inlineformset_factory(
    Plainte, PieceConviction,
    form=PieceConvictionForm,
    extra=1, 
    can_delete=True
)


class EtapeForm(forms.ModelForm):
    class Meta:
        model = EtapeProcessus
        fields = ['type_etape', 'message_public', 'commentaire_interne', 'document_joint']
        widgets = {
            'message_public': forms.Textarea(attrs={'rows': 2, 'class': 'w-full border p-2 rounded', 'placeholder': 'Message visible par le citoyen...'}),
            'commentaire_interne': forms.Textarea(attrs={'rows': 2, 'class': 'w-full border p-2 rounded bg-yellow-50', 'placeholder': 'Note interne administrative...'}),
            'document_joint': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-gov-blue file:text-white hover:file:bg-blue-900'}),
        }

    def __init__(self, *args, **kwargs):
        self.plainte_actuelle = kwargs.pop('plainte', None)
        super().__init__(*args, **kwargs)

    def clean_type_etape(self):
        new_etape = self.cleaned_data['type_etape']
        
        if self.plainte_actuelle:
            # Ordre logique strict de vos étapes
            ORDRE_LOGIQUE = [
                'DEPOT', 
                'RECEVABILITE', 
                'ENQUETE', 
                'AUDIENCE', 
                'DELIBERE', 
                'JUGEMENT', 
                'CLOTURE'
            ]
            
            # On récupère la toute dernière étape enregistrée
            last_step = self.plainte_actuelle.historique.last()
            
            if last_step:
                # Si on sélectionne REJET, c'est autorisé à tout moment (sauf si déjà clos)
                if new_etape == 'REJET':
                    if last_step.type_etape in ['CLOTURE', 'REJET']:
                        raise forms.ValidationError("Le dossier est déjà clos ou rejeté.")
                    return new_etape

                try:
                    # On compare les positions dans la liste
                    old_index = ORDRE_LOGIQUE.index(last_step.type_etape)
                    new_index = ORDRE_LOGIQUE.index(new_etape)
                    
                    # Interdiction de reculer ou de refaire la même étape
                    if new_index <= old_index:
                        raise forms.ValidationError(
                            f"Action impossible : L'étape actuelle est déjà '{last_step.get_type_etape_display()}'. "
                            f"Vous ne pouvez pas revenir à '{self.cleaned_data.get('type_etape')}'."
                        )
                except ValueError:
                    # Si une étape n'est pas dans la liste (ex: un ancien statut), on laisse passer ou on bloque selon le besoin
                    pass
        
        return new_etape