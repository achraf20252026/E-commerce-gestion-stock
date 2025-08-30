# core/forms.py
from django import forms

class ContactForm(forms.Form):
    nom = forms.CharField(max_length=100, required=True, label="Votre nom")
    email = forms.EmailField(required=True, label="Votre email")
    sujet = forms.CharField(max_length=100, required=True, label="Sujet")
    message = forms.CharField(widget=forms.Textarea, required=True, label="Votre message")