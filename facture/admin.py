from django.contrib import admin
from .models import Commande, LigneCommande, Facture

class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ('produit', 'quantite', 'prix_unitaire')

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'etat', 'date_commande', 'total')
    list_filter = ('etat', 'date_commande')
    search_fields = ('client__username', 'client__first_name')
    readonly_fields = ('date_commande', 'total')
    inlines = [LigneCommandeInline]

admin.site.register(Facture)