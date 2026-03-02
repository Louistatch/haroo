"""
Template tags pour le formatage de devise FCFA
"""

from django import template
from apps.core.currency import format_fcfa, format_fcfa_short

register = template.Library()


@register.filter(name='fcfa')
def fcfa_filter(value, decimal_places=0):
    """
    Filtre de template pour formater un montant en FCFA.
    
    Usage dans les templates:
        {{ montant|fcfa }}
        {{ montant|fcfa:2 }}  # Avec 2 décimales
    """
    try:
        decimal_places = int(decimal_places)
    except (ValueError, TypeError):
        decimal_places = 0
    
    return format_fcfa(value, use_symbol=True, decimal_places=decimal_places)


@register.filter(name='fcfa_short')
def fcfa_short_filter(value):
    """
    Filtre de template pour formater un montant FCFA de manière compacte.
    
    Usage dans les templates:
        {{ montant|fcfa_short }}
    """
    return format_fcfa_short(value)


@register.simple_tag
def format_currency(amount, currency='FCFA', decimal_places=0):
    """
    Tag de template pour formater un montant avec devise.
    
    Usage dans les templates:
        {% format_currency montant %}
        {% format_currency montant 'FCFA' 2 %}
    """
    if currency == 'FCFA':
        return format_fcfa(amount, use_symbol=True, decimal_places=decimal_places)
    else:
        # Support futur pour d'autres devises
        return f"{amount} {currency}"
