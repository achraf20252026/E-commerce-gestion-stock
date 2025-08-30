from django.conf import settings
from django.db import models
from django.utils import timezone
from ecommerce.models import Produit
from stock.models import CustomUser

class Commande(models.Model):
    class Etat(models.TextChoices):
        EN_ATTENTE = 'en_attente', 'En attente de confirmation'
        CONFIRMEE = 'confirmee', 'Confirmée'
        EXPEDIEE = 'expediee', 'Expédiée'
        TERMINEE = 'terminee', 'Terminée'
        ANNULEE = 'annulee', 'Annulée (Stock réintégré)'
        ANNULEE_CLIENT = 'annulee_client', 'Annulée par le client'
    
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='commandes')
    operateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='commandes_gerees', limit_choices_to={'role__in': [CustomUser.Role.ADMIN, CustomUser.Role.VENTE]})
    date_commande = models.DateTimeField(auto_now_add=True)
    etat = models.CharField(max_length=30, choices=Etat.choices, default=Etat.EN_ATTENTE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    adresse_livraison = models.TextField()

    def __str__(self):
        return f"Commande #{self.id} pour {self.client.get_full_name() or self.client.username}"

class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"
    
    @property
    def total_ligne(self):
        return self.quantite * self.prix_unitaire
    

class Facture(models.Model):
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE)
    num_facture = models.CharField(max_length=100, unique=True, blank=True)
    date_facture = models.DateField(auto_now_add=True)
    prix_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=20.0)
    prix_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Facture {self.num_facture}"

    def save(self, *args, **kwargs):
        if not self.num_facture:
            annee_actuelle = timezone.now().year
            derniere_facture = Facture.objects.filter(date_facture__year=annee_actuelle).order_by('num_facture').last()
            nouveau_numero = 1
            if derniere_facture:
                dernier_numero = int(derniere_facture.num_facture.split('-')[-1])
                nouveau_numero = dernier_numero + 1
            self.num_facture = f"FACT-{annee_actuelle}-{nouveau_numero:04d}"
        
        # Le calcul des totaux peut être fait dans la vue avant de sauvegarder
        super().save(*args, **kwargs)

    @property
    def montant_tva(self):
        """Calcule le montant de la TVA à partir des totaux."""
        return self.prix_ttc - self.prix_ht
