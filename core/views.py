# core/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from ecommerce.utils import send_transactional_email
from django.conf import settings

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            email = form.cleaned_data['email']
            sujet = form.cleaned_data['sujet']
            message_client = form.cleaned_data['message']

            # Préparation de l'email à envoyer à l'admin
            context = {
                'nom': nom,
                'email': email,
                'sujet': sujet,
                'message_client': message_client,
            }
            
            send_transactional_email(
                subject=f"Nouveau message de contact : {sujet}",
                template_name='emails/contact_form_notification.html',
                context=context,
                recipient_list=[settings.COMPANY_EMAIL] # On envoie à l'email de l'entreprise
            )
            
            messages.success(request, "Votre message a bien été envoyé. Nous vous répondrons dès que possible.")
            return redirect('core:contact')
    else:
        form = ContactForm()
        
    return render(request, 'core/contact.html', {'form': form})

def terms_of_service_view(request):
    return render(request, 'core/terms_of_service.html')

def privacy_policy_view(request):
    return render(request, 'core/privacy_policy.html')