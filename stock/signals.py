from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import LigneEntreeStock

@receiver(post_save, sender=LigneEntreeStock)
def update_stock_on_entry_save(sender, instance, created, **kwargs):
    if created:
        instance.produit.quantite_en_stock += instance.quantite_recue
        instance.produit.save(update_fields=['quantite_en_stock'])

@receiver(post_delete, sender=LigneEntreeStock)
def update_stock_on_entry_delete(sender, instance, **kwargs):
    instance.produit.quantite_en_stock -= instance.quantite_recue
    instance.produit.save(update_fields=['quantite_en_stock'])