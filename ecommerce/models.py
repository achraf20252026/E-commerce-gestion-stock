# ecommerce/models.py
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="Laisser vide pour une création automatique."
    )
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        default='categories/default.png'
    )

    class Meta:
        ordering = ['nom']
        verbose_name = "Catégorie"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('ecommerce:product_list_by_category', args=[self.slug])

    def __str__(self):
        return self.nom


class Fournisseur(models.Model):
    nom_societe = models.CharField(max_length=100)
    adresse = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.nom_societe


class Produit(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="Laisser vide pour une création automatique."
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="Stock Keeping Unit"
    )
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Description courte pour le SEO (max 160 caractères)."
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        related_name="produits"
    )
    fournisseur = models.ForeignKey(
        Fournisseur,
        on_delete=models.SET_NULL,
        null=True,
        related_name="produits"
    )
    quantite_en_stock = models.IntegerField(
        default=0,
        verbose_name="Quantité en stock",
        help_text="Mis à jour automatiquement."
    )
    est_actif = models.BooleanField(
        default=True,
        verbose_name="Visible sur le site ?"
    )

    class Meta:
        ordering = ['nom']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

    def get_image_principale(self):
        """
        Retourne l'objet de l'image principale, ou None s'il n'y en a pas.
        """
        image_principale = self.images.filter(principale=True).first()
        if image_principale:
            return image_principale
        return self.images.first()

    def get_absolute_url(self):
        return reverse('ecommerce:product_detail', args=[self.slug])


class Image(models.Model):
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to='produits/')
    principale = models.BooleanField(default=False)

    def __str__(self):
        return f"Image de {self.produit.nom}"
