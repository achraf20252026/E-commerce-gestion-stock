# ecommerce/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_transactional_email(subject, template_name, context, recipient_list):
    """
    Fonction générique pour envoyer des emails basés sur des templates.
    """
    try:
        html_message = render_to_string(template_name, context)
        
        send_mail(
            subject=subject,
            message='', # Le message texte est optionnel car on envoie du HTML
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        print(f"Email envoyé à {recipient_list} avec le sujet '{subject}'")
    except Exception as e:
        print(f"ERREUR lors de l'envoi de l'email : {e}")