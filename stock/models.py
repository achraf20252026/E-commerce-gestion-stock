from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

# On importe les modèles des autres apps à la fin pour éviter les importations circulaires au démarrage
# C'est une bonne pratique.

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrateur'
        VENTE = 'vente', 'Employé(e) Vente'
        STOCK = 'stock', 'Employé(e) Stock'
        CLIENT = 'client', 'Client'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username' # On garde le nom d'utilisateur pour la connexion
    REQUIRED_FIELDS = ['email'] # L'email devient obligatoire à la créatio
    
class EntreeStock(models.Model):
    fournisseur = models.ForeignKey('ecommerce.Fournisseur', on_delete=models.PROTECT, verbose_name="Fournisseur")
    date_entree = models.DateTimeField(auto_now_add=True, verbose_name="Date de l'entrée")
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, limit_choices_to={'role__in': [CustomUser.Role.ADMIN, CustomUser.Role.STOCK]})
    facture_fournisseur_scan = models.FileField(upload_to='factures_fournisseurs/%Y/%m/', blank=True, null=True)

    def __str__(self):
        return f"Entrée de stock de {self.fournisseur.nom_societe} le {self.date_entree.strftime('%d/%m/%Y')}"

class LigneEntreeStock(models.Model):
    entree_stock = models.ForeignKey(EntreeStock, on_delete=models.CASCADE, related_name="lignes")
    produit = models.ForeignKey('ecommerce.Produit', on_delete=models.PROTECT)
    quantite_recue = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantite_recue} x {self.produit.nom}"