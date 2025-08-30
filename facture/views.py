# facture/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# On créera ce décorateur plus tard, pour l'instant @login_required suffit

@login_required 
def dashboard_vente(request):
    # Plus tard, on ajoutera ici la logique pour récupérer les commandes à traiter
    context = {
        'commandes_en_attente': 5 # Exemple
    }
    return render(request, 'facture/dashboard_vente.html', context)

