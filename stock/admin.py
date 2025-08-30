# classTelecom/stock/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, EntreeStock, LigneEntreeStock

# Pour afficher les lignes d'entrée directement dans la page d'une entrée de stock
class LigneEntreeStockInline(admin.TabularInline):
    model = LigneEntreeStock
    extra = 1 # Affiche une ligne vide par défaut pour en ajouter une nouvelle
    autocomplete_fields = ['produit'] # Aide à chercher les produits facilement

@admin.register(EntreeStock)
class EntreeStockAdmin(admin.ModelAdmin):
    list_display = ('id', 'fournisseur', 'date_entree', 'responsable')
    list_filter = ('date_entree', 'fournisseur')
    search_fields = ('fournisseur__nom_societe',)
    inlines = [LigneEntreeStockInline]

# Amélioration de l'affichage de CustomUser dans l'admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Ajoute le champ 'role' à l'affichage dans la liste des utilisateurs
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    # Ajoute le champ 'role' aux filtres
    list_filter = ('role', 'is_staff', 'is_superuser', 'groups')
    # Ajoute le champ 'role' et 'telephone' dans le formulaire d'édition
    fieldsets = UserAdmin.fieldsets + (
        ('Informations personnalisées', {'fields': ('role', 'telephone')}),
    )

# Enregistre CustomUser avec la configuration personnalisée
admin.site.register(CustomUser, CustomUserAdmin)