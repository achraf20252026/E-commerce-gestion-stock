# accounts/forms.py
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from stock.models import CustomUser
from django import forms

class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'telephone' ,'email')

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True # Activer le compte immédiatement
        user.role = CustomUser.Role.CLIENT # Assigner le rôle "Client" par défaut
        if commit:
            user.save()
        return user
    
    def clean_email(self):
        """
        Nettoie et normalise l'adresse e-mail en la mettant en minuscules.
        """
        email = self.cleaned_data.get('email')
        if email:
            return email.lower()
        return email
    

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telephone']
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Adresse e-mail',
            'telephone': 'Numéro de téléphone'
        }

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        # On rend le champ email non modifiable après l'initialisation du formulaire
        self.fields['email'].disabled = True


