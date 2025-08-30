# ecommerce/forms.py
from django import forms
from django.conf import settings

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, settings.MAX_PRODUCT_QUANTITY_PER_ORDER + 1)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
                    choices=PRODUCT_QUANTITY_CHOICES,
                    coerce=int,
                    label='Quantité'
                )
    update = forms.BooleanField(required=False,
                                initial=False,
                                widget=forms.HiddenInput)
    

class SearchForm(forms.Form):
    query = forms.CharField(
        label='', # On ne veut pas de label à côté du champ
        widget=forms.TextInput(attrs={'placeholder': 'Rechercher un produit...'})
    )