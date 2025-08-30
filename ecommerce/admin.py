from django.contrib import admin
from .models import Categorie, Fournisseur, Produit, Image



class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'quantite_en_stock', 'categorie', 'est_actif')
    list_filter = ('categorie', 'est_actif')
    search_fields = ('nom', 'sku')
    readonly_fields = ('quantite_en_stock',) # Pour que personne ne le modifie manuellement
    inlines = [ImageInline]

admin.site.register(Categorie)
admin.site.register(Fournisseur)