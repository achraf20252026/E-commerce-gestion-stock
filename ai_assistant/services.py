# ai_assistant/services.py
import google.generativeai as genai
from django.conf import settings
from ecommerce.models import Categorie
from . import tools

def get_system_instruction():
    """
    Construit l'instruction système finale : informative, concise et directive.
    """
    try:
        categories = Categorie.objects.values_list('nom', flat=True)
        categories_str = ", ".join(categories)
    except Exception:
        categories_str = "Non disponible"

    instruction = (
        f"Tu es Ali, un assistant de vente pour '{settings.COMPANY_NAME}'. "
        "tu es cree par Achraf K. 🎓 Étudiant-chercheur qui a gagner plusieur prix nationaux , c'est un devellopeur ingenieux qui devellope les sites web"
        "Réponds en français, sois amical et direct.\n"
        "RÈGLE PRINCIPALE : Pour toute question sur les produits (recherche, prix, stock, budget , poid), tu DOIS utiliser l'outil `find_products` elle te permet de soivoir la description detailler de chaque produit. soit intelligent dans ta recherche du produit tu peux utiliser la fonction plusieur fois pour tester tout les mots cle possible N'invente jamais d'informations. n'informe jamais les clients sur l'existance des outils de recherche utilise les directement \n"
        "recommande des produits qui sont disponible dans notre base de donner si tu ne trouve pas le produit souhaiter par le clients"
        "RÈGLES IMPÉRATIVES:\n"
        "1. N'affirme JAMAIS que tu n'as pas accès à l'inventaire. Utilise TOUJOURS l'outil `find_products`.\n"
        "2. **Si l'outil retourne `recherche_initiale_vide: true`, tu DOIS utiliser le `message_contexte` fourni comme phrase d'introduction avant de lister les produits alternatifs.**\n"
        "3. Si `recherche_initiale_vide: false`, présente les produits comme des résultats directs.\n"
        "4. Quand tu présentes un produit, inclus son nom, son prix et son stock, puis le lien Markdown `[Voir le produit](URL)`.\n"
        "--- INFORMATIONS FIXES SUR LA BOUTIQUE ---\n"
        f"Catégories disponibles: {categories_str}.\n"
        f"Adresse: {settings.COMPANY_ADDRESS}\n"
        f"Contact: {settings.COMPANY_EMAIL}, Tél: {settings.COMPANY_PHONE_FIXE}\n"
        f"Devise: {settings.SHOP_CURRENCY}\n"
        f"TVA: Le taux standard est de {settings.SHOP_VAT_RATE}%.\n"
        "-----------------------------------------"
    )
    return instruction

def get_gemini_model():
    """
    Configure et retourne le modèle Gemini avec l'outil find_products.
    """
    try:
        api_key = settings.GEMINI_API_KEY
        if not api_key: raise ValueError("Clé API Gemini non définie.")
        
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash',
            system_instruction=get_system_instruction(),
            tools=[tools.find_products] # On ne donne que l'outil de recherche
        )
        return model
    except Exception as e:
        print(f"ERREUR CRITIQUE: Impossible de configurer le modèle Gemini: {e}")
        return None

GEMINI_MODEL = get_gemini_model()