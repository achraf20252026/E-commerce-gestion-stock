from django.urls import path
from . import views

app_name = 'facture'

urlpatterns = [
    path('dashboard/', views.dashboard_vente, name='dashboard_vente'),
]