from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('boutique/', views.product_list, name='product_list'), 
    path('categorie/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('recherche/', views.product_list, name='search_results'),
    path('produit/<slug:product_slug>/', views.product_detail, name='product_detail'),

    path('panier/', views.cart_detail, name='cart_detail'),
    path('panier/ajouter/<int:product_id>/', views.cart_add, name='cart_add'),
    path('panier/supprimer/<int:product_id>/', views.cart_remove, name='cart_remove'),

    path('commande/finaliser/', views.checkout, name='checkout'),
    path('commande/succes/', views.order_success, name='order_success'),

]