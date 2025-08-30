from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts' 

urlpatterns = [

    path('connexion/', views.login_view, name='login'),
    path('inscription/', views.signup_view, name='signup'),
    path('deconnexion/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    path('profil/', views.profile_view, name='profile'),
    path('commandes/', views.order_history_view, name='order_history'),
    path('commandes/annuler/<int:order_id>/', views.cancel_order_view, name='cancel_order'),
    path('commandes/facture/<int:order_id>/', views.view_invoice_view, name='view_invoice'),

    path('changer-mot-de-passe/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change_form.html',
        success_url='/compte/changer-mot-de-passe/fait/' # URL vers laquelle rediriger après succès
    ), name='password_change'),
    
    path('changer-mot-de-passe/fait/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name='password_change_done'),


    path('reinitialiser-mot-de-passe/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html',
             email_template_name='emails/password_reset_email.html', # Note: on déplace ce template
             subject_template_name='emails/password_reset_subject.txt', # et celui-ci
             success_url='/compte/reinitialiser-mot-de-passe/envoye/'
         ),
         name='password_reset'), # <<-- C'est ce 'name' qui manquait et causait l'erreur
    
    path('reinitialiser-mot-de-passe/envoye/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('reinitialiser/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/compte/reinitialiser-mot-de-passe/complet/'
         ),
         name='password_reset_confirm'),
    
    path('reinitialiser-mot-de-passe/complet/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    
]