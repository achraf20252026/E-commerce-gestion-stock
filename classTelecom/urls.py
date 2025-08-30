# classTelecom/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from ecommerce.sitemaps import ProduitSitemap, CategorieSitemap

sitemaps = {
    'produits': ProduitSitemap,
    'categories': CategorieSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- On regroupe les applications "métier" ---
    path('compte/', include('accounts.urls')),
    path('assistant/', include('ai_assistant.urls', namespace='ai_assistant')),
    
    # --- On regroupe les applications de gestion ---
    path('gestion/ventes/', include('facture.urls', namespace='facture')),
    path('gestion/', include('stock.urls', namespace='stock')), 
    
    # --- On ajoute les pages statiques ici. Elles auront des préfixes comme /contact/ ---
    path('', include('core.urls')), # On laisse 'core' gérer ses propres préfixes

    # --- L'application principale e-commerce est à la fin pour la racine '/' ---
    path('', include('ecommerce.urls', namespace='ecommerce')),
    
    # --- URLs techniques ---
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)