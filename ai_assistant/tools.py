# ai_assistant/tools.py
from ecommerce.models import Produit
from django.db.models import Q
import json

def find_products(query: str = None, category_name: str = None, prix_max: float = None, prix_min: float = None):
    """
    Recherche des produits par mot-clé, catégorie et/ou budget.
    Si aucun produit ne correspond, il essaiera de trouver des alternatives pertinentes à recommander.

    Args:
        query (str, optional): Terme de recherche (nom du produit, marque, etc.).
        category_name (str, optional): Nom de la catégorie pour filtrer.
        prix_max (float, optional): Le PRIX MAXIMUM.
        prix_min (float, optional): Le PRIX MINIMUM.
    """
    base_queryset = Produit.objects.filter(est_actif=True)
    produits = base_queryset
    
    # --- APPLICATION DES FILTRES INITIAUX ---
    if category_name:
        produits = produits.filter(categorie__nom__iexact=category_name)
    if prix_max is not None:
        produits = produits.filter(prix__lte=prix_max)
    if prix_min is not None:
        produits = produits.filter(prix__gte=prix_min)
    
    if query:
        keywords = query.lower().split()
        q_objects = Q()
        for keyword in keywords:
            q_objects &= (Q(nom__icontains=keyword) | Q(description__icontains=keyword))
        produits = produits.filter(q_objects)

    # --- LOGIQUE DE FALLBACK EN PLUSIEURS ÉTAPES ---
    is_fallback = False
    fallback_message = ""

    if not produits.exists():
        is_fallback = True
        print(f"Recherche stricte vide. Lancement du fallback...")
        
        # Stratégie 1 : Élargir la fourchette de prix de 20%
        if prix_max is not None:
            prix_elargi = prix_max * 1.20
            produits = base_queryset.filter(prix__lte=prix_elargi)
            if query:
                 produits = produits.filter(q_objects)
            if category_name:
                 produits = produits.filter(categorie__nom__iexact=category_name)

            if produits.exists():
                fallback_message = f"Je n'ai rien trouvé dans votre budget exact, mais voici des options un peu au-dessus qui pourraient vous intéresser."
        
        # Stratégie 2 (si la 1 a échoué) : Ignorer le budget et ne chercher que par mot-clé/catégorie
        if not produits.exists():
            produits = base_queryset
            if query:
                 produits = produits.filter(q_objects)
            if category_name:
                 produits = produits.filter(categorie__nom__iexact=category_name)
            
            if produits.exists():
                fallback_message = "Je n'ai rien trouvé dans cette gamme de prix, mais voici d'autres produits similaires qui pourraient correspondre."

        # Stratégie 3 (dernier recours) : Montrer les produits les plus populaires de la boutique
        if not produits.exists():
            # (Pour l'instant, on prend des produits au hasard, plus tard on pourra avoir un champ "populaire")
            produits = base_queryset.order_by('?')
            fallback_message = "Je n'ai pas trouvé ce que vous cherchez. Voici cependant quelques-uns de nos produits les plus populaires."
    
    # --- PRÉPARATION DE LA RÉPONSE ---
    if not produits.exists():
        return json.dumps({"produits": [], "message": "Désolé, je n'ai vraiment trouvé aucun produit pertinent à vous proposer."})
        
    produits_data = []
    for p in produits.order_by('prix')[:3]: # Limiter à 3 pour des recommandations concises
        produits_data.append({
            "nom": p.nom,
            "prix": float(p.prix),
            "stock": "En stock" if p.quantite_en_stock > 0 else "Épuisé",
            "categorie": p.categorie.nom,
            "url": p.get_absolute_url()
        })
        
    response_data = {
        "produits": produits_data,
        "recherche_initiale_vide": is_fallback,
        "message_contexte": fallback_message # Message que l'IA doit utiliser
    }
    
    return json.dumps(response_data)