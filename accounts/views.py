from django.shortcuts import render, redirect
from django.contrib.auth import login , authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileUpdateForm
from facture.models import Commande
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .utils import send_email_async

def login_view(request):
    # Si l'utilisateur est déjà connecté, on le redirige immédiatement
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('stock:dashboard') # L'admin va au dashboard principal
        elif request.user.role == 'vente':
            return redirect('facture:dashboard_vente') # Le vendeur va à son dashboard
        elif request.user.role == 'stock':
            return redirect('stock:dashboard') # Le gestionnaire de stock aussi
        else: # Client
            return redirect('ecommerce:product_list')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'admin':
                return redirect('stock:dashboard') # L'admin va au dashboard principal
            elif user.role == 'vente':
                return redirect('facture:dashboard_vente') # Le vendeur va à son dashboard
            elif user.role == 'stock':
                return redirect('stock:dashboard') # Le gestionnaire de stock aussi
            else: # Client
                return redirect('ecommerce:product_list')
    else:
        form = AuthenticationForm()
        form.fields['username'].label = "Nom d'utilisateur ou Email" # On change le label ici
        
    return render(request, 'accounts/login.html', {'form': form, 'page_title': "Connexion"})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            # --- ENVOI DE L'EMAIL (ASYNCHRONE) ---
            current_site = get_current_site(request)
            send_email_async(
                subject="Bienvenue sur Class Telecom !",
                template_name='emails/bienvenue.html',
                context={'user': user, 'domain': current_site.domain},
                recipient_list=[user.email]
            )
            # --------------------------------------

            messages.success(request, f"Bienvenue, {user.username}! Votre compte a été créé avec succès.")
            return redirect('/')
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        # Si le formulaire est soumis, on le traite
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès !')
            return redirect('accounts:profile') # On redirige pour éviter le re-post du formulaire
    else:
        # Sinon, on affiche le formulaire pré-rempli avec les infos de l'utilisateur
        form = ProfileUpdateForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def order_history_view(request):
    # On récupère toutes les commandes du client connecté, de la plus récente à la plus ancienne
    commandes = Commande.objects.filter(client=request.user).order_by('-date_commande')
    context = {
        'commandes': commandes
    }
    return render(request, 'accounts/order_history.html', context)


@login_required
@require_POST
def cancel_order_view(request, order_id):
    commande = get_object_or_404(Commande, id=order_id, client=request.user)
    
    if commande.etat == Commande.Etat.EN_ATTENTE:
        # On utilise le nouvel état spécifique au client
        commande.etat = Commande.Etat.ANNULEE_CLIENT
        commande.save(update_fields=['etat'])
        messages.success(request, f"La commande #{commande.id} a été annulée avec succès.")
    else:
        messages.error(request, f"Impossible d'annuler la commande #{commande.id} car elle a déjà été traitée.")
        
    return redirect('accounts:order_history')

@login_required
def view_invoice_view(request, order_id):
    # On s'assure que la commande appartient bien au client
    commande = get_object_or_404(Commande, id=order_id, client=request.user)
    
    # On s'assure que la commande est terminée et que la facture existe
    if commande.etat != Commande.Etat.TERMINEE or not hasattr(commande, 'facture'):
        messages.error(request, "La facture pour cette commande n'est pas encore disponible.")
        return redirect('accounts:order_history')
    
    facture = commande.facture
    
    context = {
        'facture': facture
    }
    # On rend un template HTML normal
    return render(request, 'accounts/invoice_template.html', context)