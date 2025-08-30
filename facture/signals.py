# facture/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Commande, Facture
from decimal import Decimal
from django.conf import settings
from ecommerce.utils import send_transactional_email

@receiver(pre_save, sender=Commande)
def update_stock_on_order_status_change(sender, instance, **kwargs):
    if not instance.pk: # Ne rien faire si c'est une nouvelle commande
        return

    try:
        ancienne_commande = Commande.objects.get(pk=instance.pk)
    except Commande.DoesNotExist:
        return
    
    etats_non_confirmes = [Commande.Etat.EN_ATTENTE]
    
    # --- LOGIQUE DE DÉCRÉMENTATION AVEC VÉRIFICATION PRÉALABLE ---
    if instance.etat == Commande.Etat.CONFIRMEE and ancienne_commande.etat in etats_non_confirmes:
        
        # 1. On VÉRIFIE d'abord si on a assez de stock pour TOUTE la commande
        for ligne in instance.lignes.all():
            if ligne.produit.quantite_en_stock < ligne.quantite:
                # Si le stock est insuffisant pour un seul article, on bloque TOUT.
                # Le message d'erreur sera visible par l'employé dans l'interface /admin/ de Django.
                raise ValueError(
                    f"Impossible de confirmer la commande #{instance.id}. "
                    f"Stock insuffisant pour le produit '{ligne.produit.nom}'. "
                    f"Quantité demandée : {ligne.quantite}, Quantité disponible : {ligne.produit.quantite_en_stock}."
                )
    
    if instance.etat == Commande.Etat.TERMINEE and ancienne_commande.etat != Commande.Etat.TERMINEE:
        if not hasattr(instance, 'facture'):
            prix_ttc = instance.total
            tva_pourcentage = settings.SHOP_VAT_RATE
            montant_tva = prix_ttc * (tva_pourcentage / 100)
            prix_ht = prix_ttc - montant_tva
            
            Facture.objects.create(
                commande=instance, prix_ht=prix_ht, tva=tva_pourcentage, prix_ttc=prix_ttc
            )
        
        # 2. Si toutes les vérifications sont passées, on DÉCRÉMENTE le stock
        for ligne in instance.lignes.all():
            ligne.produit.quantite_en_stock -= ligne.quantite
            ligne.produit.save(update_fields=['quantite_en_stock'])

    # --- LOGIQUE DE RÉINTÉGRATION DU STOCK (ne change pas) ---
    if instance.etat == Commande.Etat.ANNULEE and ancienne_commande.etat == Commande.Etat.CONFIRMEE:
        for ligne in instance.lignes.all():
            ligne.produit.quantite_en_stock += ligne.quantite
            ligne.produit.save(update_fields=['quantite_en_stock'])




@receiver(pre_save, sender=Commande)
def update_stock_and_create_invoice(sender, instance, **kwargs):
    if not instance.pk: return
    try:
        ancienne_commande = Commande.objects.get(pk=instance.pk)
    except Commande.DoesNotExist:
        return
    
    # On envoie un email si le statut a réellement changé
    if instance.etat != ancienne_commande.etat:
        # On exclut l'état initial pour ne pas envoyer d'email en double
        if instance.etat != Commande.Etat.EN_ATTENTE:
            send_transactional_email(
                subject=f"Mise à jour de votre commande #{instance.id}",
                template_name='emails/changement_statut_commande.html',
                context={'commande': instance},
                recipient_list=[instance.client.email]
            )