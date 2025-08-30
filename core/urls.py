# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('contact/', views.contact_view, name='contact'),
    path('conditions-generales-vente/', views.terms_of_service_view, name='terms'),
    path('politique-confidentialite/', views.privacy_policy_view, name='privacy'),
]