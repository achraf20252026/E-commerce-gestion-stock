# ecommerce/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string, TemplateDoesNotExist
from django.conf import settings
import threading 

def send_transactional_email(subject, template_name, context, recipient_list):
    """
    Fonction de débogage pour l'envoi d'emails.
    """
    print("--- DÉBUT DE L'ENVOI D'EMAIL ---")
    print(f"Sujet : {subject}")
    print(f"Template : {template_name}")
    print(f"Destinataires : {recipient_list}")
    
    # Vérification 1: Les destinataires sont-ils valides ?
    if not recipient_list or not all(recipient_list):
        print("ERREUR : La liste des destinataires est vide ou invalide.")
        return

    try:
        # Vérification 2: Le template peut-il être rendu ?
        print("Tentative de rendu du template HTML...")
        html_message = render_to_string(template_name, context)
        print("Rendu du template réussi.")
        
        # Vérification 3: L'envoi lui-même
        print("Tentative d'envoi via send_mail...")
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False, # Force l'affichage de toute erreur
        )
        print("Email envoyé avec succès (selon Django).")

    except TemplateDoesNotExist:
        print(f"ERREUR CRITIQUE : Le template d'email '{template_name}' est introuvable.")
    except Exception as e:
        # Affiche n'importe quelle autre erreur qui pourrait survenir
        print(f"ERREUR CRITIQUE lors de l'envoi de l'email : {e}")
        # Vous pouvez même ajouter un import pdb; pdb.set_trace() ici pour un débogage interactif
    
    print("--- FIN DE L'ENVOI D'EMAIL ---")




def send_email_async(subject, template_name, context, recipient_list):
    """Envoie un email dans un thread séparé (non bloquant)."""
    thread = threading.Thread(
        target=send_transactional_email,
        args=(subject, template_name, context, recipient_list)
    )
    thread.start()
