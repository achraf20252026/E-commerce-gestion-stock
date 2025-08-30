# ecommerce/context_processors.py
from .cart import Cart
from django.conf import settings
from .forms import SearchForm

def cart(request):
    return {'cart': Cart(request)}

def site_config(request):
    return {
        'COMPANY_NAME': settings.COMPANY_NAME,
        'COMPANY_ADDRESS': settings.COMPANY_ADDRESS,
        'COMPANY_EMAIL': settings.COMPANY_EMAIL,
        'COMPANY_PHONE_FIXE': settings.COMPANY_PHONE_FIXE,
        'COMPANY_PHONE_MOBILE': settings.COMPANY_PHONE_MOBILE,
        'SHOP_CURRENCY': settings.SHOP_CURRENCY,
        'search_form': SearchForm(),
    }