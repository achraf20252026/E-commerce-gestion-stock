# ecommerce/cart.py
from decimal import Decimal
from django.conf import settings
from .models import Produit

class Cart:
    def __init__(self, request):
        """
        Initialise le panier.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Sauvegarde un panier vide dans la session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
            """
            Ajoute un produit ou met à jour la quantité.
            Retourne True en cas de succès, False en cas d'échec (stock insuffisant).
            """
            product_id = str(product.id)
            
            # Déterminer la quantité finale souhaitée
            if update_quantity:
                final_quantity = quantity
            else:
                current_quantity = self.cart.get(product_id, {}).get('quantity', 0)
                final_quantity = current_quantity + quantity

            # Vérification unique et claire du stock
            if product.quantite_en_stock < final_quantity:
                return False # Échec : stock insuffisant

            if product_id not in self.cart:
                self.cart[product_id] = {'quantity': 0, 'price': str(product.prix)}
            
            self.cart[product_id]['quantity'] = final_quantity
            self.save()
            return True # Succès

    def save(self):
        # Marque la session comme "modifiée" pour s'assurer qu'elle est sauvegardée
        self.session.modified = True

    def remove(self, product):
        """
        Supprime un produit du panier.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Permet de boucler sur les articles du panier et récupère les produits
        depuis la base de données.
        """
        product_ids = self.cart.keys()
        # Récupère les objets produits et les ajoute au panier
        products = Produit.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Compte tous les articles dans le panier.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # Supprime le panier de la session
        try:
            del self.session[settings.CART_SESSION_ID]
            self.save()
        except KeyError:
            pass