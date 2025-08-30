# ecommerce/templatetags/url_helpers.py
from django import template

register = template.Library()


@register.filter
def mul(value, arg):
    """Multiplie la valeur par l'argument."""
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    
    # Si 'page' est un des nouveaux kwargs, on l'accepte.
    # Sinon, si on change le 'sort' ou le 'query', on supprime 'page' pour revenir à la page 1.
    if 'page' not in kwargs and ('sort' in kwargs or 'query' in kwargs):
        query.pop('page', None)

    for key, value in kwargs.items():
        query[key] = value
        
    return query.urlencode()