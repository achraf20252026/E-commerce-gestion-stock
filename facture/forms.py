# facture/forms.py
from django import forms
from .models import Commande

class CommandeConnecteForm(forms.ModelForm):
    """Formulaire pour un utilisateur déjà connecté."""
    class Meta:
        model = Commande
        fields = ['adresse_livraison']
        widgets = {'adresse_livraison': forms.Textarea(attrs={'rows': 3})}

class CommandeInviteForm(forms.Form):
    """Formulaire pour un invité, qui inclut la création de compte."""
    prenom = forms.CharField(max_length=100)
    nom = forms.CharField(max_length=100)
    email = forms.EmailField()
    telephone = forms.CharField(max_length=20, required=False)
    adresse_livraison = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))


    def clean_email(self):
        """
        Nettoie et normalise l'adresse e-mail en la mettant en minuscules.
        """
        email = self.cleaned_data.get('email')
        if email:
            return email.lower()
        return email