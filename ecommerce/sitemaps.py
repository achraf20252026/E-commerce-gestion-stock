# ecommerce/sitemaps.py
from django.contrib.sitemaps import Sitemap
from .models import Produit, Categorie

class ProduitSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        # Retourne tous les produits actifs que l'on veut indexer
        return Produit.objects.filter(est_actif=True)

    # lastmod n'est pas nécessaire sauf si vous avez un champ de date de modification

class CategorieSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Categorie.objects.all()