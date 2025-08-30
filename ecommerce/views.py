# ecommerce/views.py
from django.conf import settings
from django.contrib.auth.decorators import login_required
from accounts.utils import send_transactional_email , send_email_async

from facture.models import Commande, LigneCommande 
from facture.forms import CommandeConnecteForm, CommandeInviteForm
from accounts import forms
from django.shortcuts import render, redirect, get_object_or_404
from .models import Produit
from django.views.decorators.http import require_POST
from .models import Produit
from .cart import Cart
from .forms import CartAddProductForm
from django.contrib import messages

from django.contrib.auth import login
from stock.models import CustomUser 
import uuid 
from django.contrib.sites.shortcuts import get_current_site

# ecommerce/views.py
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Categorie, Produit
from django.db.models import Q
from django.urls import reverse


def home_page(request):
    """
    Vue pour la page d'accueil.
    Fournit les catégories et une sélection de produits phares.
    """
    categories = Categorie.objects.all()
    # On prend 4 produits actifs au hasard pour la section "Produits Phares"
    produits_phares = Produit.objects.filter(est_actif=True, quantite_en_stock__gt=0).order_by('?')[:4]

    context = {
        'categories': categories,
        'produits_phares': produits_phares,
    }
    return render(request, 'ecommerce/home_page.html', context)


def product_list(request, category_slug=None):
    """
    Vue UNIFIÉE pour lister les produits.
    Gère le filtrage par catégorie, la recherche, le tri, la pagination et le fil d'Ariane.
    """
    categorie = None
    categories = Categorie.objects.all()
    produits = Produit.objects.filter(est_actif=True)
    query = request.GET.get('query')

    # --- FILTRAGE ---
    if category_slug:
        categorie = get_object_or_404(Categorie, slug=category_slug)
        produits = produits.filter(categorie=categorie)
    
    if query:
        # On divise la requête en mots-clés
        keywords = query.split()
        # On construit une requête qui doit contenir TOUS les mots-clés (logique AND)
        q_objects = Q()
        for keyword in keywords:
            q_objects &= (
                Q(nom__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(categorie__nom__icontains=keyword) |
                Q(fournisseur__nom_societe__icontains=keyword)
            )
        produits = produits.filter(q_objects).distinct()

    # --- LOGIQUE DE TRI AMÉLIORÉE ---
    sort = request.GET.get('sort', 'name_asc') # 'name_asc' est maintenant le tri par défaut
    
    if sort == 'price_asc':
        produits = produits.order_by('prix')
    elif sort == 'price_desc':
        produits = produits.order_by('-prix')
    elif sort == 'name_desc':
        produits = produits.order_by('-nom')
    else: # Tri par défaut (name_asc)
        produits = produits.order_by('nom')

    # --- PAGINATION ---
    paginator = Paginator(produits, settings.PRODUCTS_PER_PAGE)
    page_number = request.GET.get('page')
    try:
        produits_pagines = paginator.page(page_number)
    except PageNotAnInteger:
        produits_pagines = paginator.page(1)
    except EmptyPage:
        produits_pagines = paginator.page(paginator.num_pages)

    # --- FIL D'ARIANE ---
    breadcrumbs = [{'name': 'Accueil', 'url': reverse('ecommerce:home_page')}]
    if categorie:
        breadcrumbs.append({'name': categorie.nom, 'url': categorie.get_absolute_url()})
    elif not query:
        breadcrumbs.append({'name': 'Boutique', 'url': reverse('ecommerce:product_list')})

    context = {
        'categorie': categorie,
        'categories': categories,
        'produits': produits_pagines,
        'sort': sort,
        'query': query,
        'breadcrumbs': breadcrumbs,  # <-- On ajoute le fil d'Ariane au contexte
    }
    
    return render(request, 'ecommerce/product_list.html', context)


def product_detail(request, product_slug):
    """
    Vue pour afficher le détail d'un produit avec :
    - formulaire d'ajout au panier
    - fil d'Ariane
    - produits similaires
    """
    produit = get_object_or_404(Produit, slug=product_slug, est_actif=True)
    cart_product_form = CartAddProductForm()

    # --- SÉLECTION DES PRODUITS SIMILAIRES ---
    produits_similaires = Produit.objects.filter(
        categorie=produit.categorie,
        est_actif=True
    ).exclude(pk=produit.pk).order_by('?')[:4]  # 4 produits aléatoires

    # --- FIL D'ARIANE ---
    breadcrumbs = [
        {'name': 'Accueil', 'url': reverse('ecommerce:home_page')},
        {'name': produit.categorie.nom, 'url': produit.categorie.get_absolute_url()},
        {'name': produit.nom, 'url': '#'}  # Dernier élément sans lien
    ]

    context = {
        'produit': produit,
        'cart_product_form': cart_product_form,
        'breadcrumbs': breadcrumbs,
        'produits_similaires': produits_similaires,  # <-- ajouté au contexte
    }
    return render(request, 'ecommerce/product_detail.html', context)

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'ecommerce/cart_detail.html', {'cart': cart})

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    produit = get_object_or_404(Produit, id=product_id)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        
        # La méthode add retourne maintenant True ou False
        success = cart.add(product=produit,
                           quantity=cd['quantity'],
                           update_quantity=cd['update'])
        
        if success:
            if cd['update']:
                messages.success(request, f"La quantité pour <strong>{produit.nom}</strong> a été mise à jour.")
            else:
                messages.success(request, f"<strong>{produit.nom}</strong> a été ajouté à votre panier.")
        else:
            messages.error(request, f"Stock insuffisant pour <strong>{produit.nom}</strong>. Quantité disponible : {produit.quantite_en_stock}.")

    # On redirige vers la page d'où vient l'utilisateur, ou le panier par défaut
    return redirect(request.POST.get('next', 'ecommerce:cart_detail'))

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    produit = get_object_or_404(Produit, id=product_id)
    cart.remove(produit)
    messages.info(request, f"<strong>{produit.nom}</strong> a été retiré de votre panier.")
    return redirect('ecommerce:cart_detail')

def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Votre panier est vide.")
        return redirect('ecommerce:product_list')

    # Initialisation du formulaire
    if request.user.is_authenticated:
        form = CommandeConnecteForm(request.POST or None)
    else:
        form = CommandeInviteForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = request.user
            is_new_user = False  # Flag pour savoir si on doit envoyer l'email de bienvenue

            # --- Cas invité : création du compte ---
            if not user.is_authenticated:
                email = form.cleaned_data['email']
                if CustomUser.objects.filter(email=email).exists():
                    messages.error(request, "Un compte existe déjà avec cet email. Veuillez vous connecter.")
                    return redirect(f"{settings.LOGIN_URL}?next={request.path}")

                password = str(uuid.uuid4())
                username = email.split('@')[0] + str(uuid.uuid4())[:4]

                user = CustomUser.objects.create_user(
                    username=username, email=email, password=password,
                    first_name=form.cleaned_data['prenom'],
                    last_name=form.cleaned_data['nom'],
                    telephone=form.cleaned_data.get('telephone', '')
                )
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                is_new_user = True

            # --- Création de la commande ---
            commande = Commande.objects.create(
                client=user,
                adresse_livraison=form.cleaned_data['adresse_livraison'],
                total=cart.get_total_price()
            )

            for item in cart:
                LigneCommande.objects.create(
                    commande=commande,
                    produit=item['product'],
                    quantite=item['quantity'],
                    prix_unitaire=item['price']
                )

            # --- GESTION DES EMAILS (ASYNCHRONE) ---

            # 1. Email de bienvenue (si nouvel utilisateur)
            if is_new_user:
                current_site = get_current_site(request)
                send_email_async(
                    subject="Votre compte a été créé sur Class Telecom",
                    template_name='emails/bienvenue.html',
                    context={'user': user, 'domain': current_site.domain},
                    recipient_list=[user.email]
                )

            # 2. Email de confirmation de commande
            send_email_async(
                subject=f"Confirmation de votre commande #{commande.id}",
                template_name='emails/confirmation_commande.html',
                context={'user': user, 'commande': commande},
                recipient_list=[user.email]
            )

            # 3. Email aux admins/gestionnaires
            emails_gestionnaires = CustomUser.objects.filter(
                role__in=[CustomUser.Role.ADMIN, CustomUser.Role.VENTE]
            ).values_list('email', flat=True)

            if emails_gestionnaires:
                send_email_async(
                    subject=f"Nouvelle commande #{commande.id} à traiter",
                    template_name='emails/nouvelle_commande_admin.html',
                    context={'commande': commande},
                    recipient_list=list(emails_gestionnaires)
                )

            # --- Nettoyage et redirection ---
            cart.clear()
            request.session['order_id'] = commande.id
            return redirect('ecommerce:order_success')

    return render(request, 'ecommerce/checkout.html', {'cart': cart, 'form': form})


def order_success(request):
    # On récupère l'ID de la commande depuis la session pour l'afficher
    order_id = request.session.get('order_id')
    
    # C'est une bonne pratique de supprimer l'ID de la session après l'avoir utilisé
    # pour éviter de le réafficher si l'utilisateur recharge la page de succès plus tard.
    if 'order_id' in request.session:
        del request.session['order_id']

    context = {
        'order_id': order_id
    }
    return render(request, 'ecommerce/order_success.html', context)

