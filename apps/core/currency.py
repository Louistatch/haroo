"""
Utilitaires de formatage de devise pour le Franc CFA (FCFA)
Conforme à l'exigence 38.3
"""

from decimal import Decimal
from django.utils.formats import number_format


def format_fcfa(amount, use_symbol=True, decimal_places=0):
    """
    Formate un montant en Francs CFA avec le format togolais.
    
    Args:
        amount: Montant à formater (Decimal, float ou int)
        use_symbol: Si True, ajoute le symbole FCFA
        decimal_places: Nombre de décimales (0 par défaut pour FCFA)
    
    Returns:
        str: Montant formaté (ex: "1 000 FCFA" ou "1 500,50 FCFA")
    
    Examples:
        >>> format_fcfa(1000)
        '1 000 FCFA'
        >>> format_fcfa(1500.50, decimal_places=2)
        '1 500,50 FCFA'
        >>> format_fcfa(1000, use_symbol=False)
        '1 000'
    """
    if amount is None:
        return "0 FCFA" if use_symbol else "0"
    
    # Convertir en Decimal pour précision
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    
    # Formater le nombre avec séparateurs français
    formatted = number_format(
        amount,
        decimal_pos=decimal_places,
        use_l10n=True,
        force_grouping=True
    )
    
    # Ajouter le symbole FCFA si demandé
    if use_symbol:
        return f"{formatted} FCFA"
    
    return formatted


def parse_fcfa(amount_str):
    """
    Parse une chaîne de caractères représentant un montant FCFA.
    
    Args:
        amount_str: Chaîne à parser (ex: "1 000 FCFA", "1500,50")
    
    Returns:
        Decimal: Montant parsé
    
    Examples:
        >>> parse_fcfa("1 000 FCFA")
        Decimal('1000')
        >>> parse_fcfa("1 500,50")
        Decimal('1500.50')
    """
    if not amount_str:
        return Decimal('0')
    
    # Nettoyer la chaîne
    cleaned = str(amount_str).strip()
    
    # Retirer le symbole FCFA
    cleaned = cleaned.replace('FCFA', '').strip()
    
    # Retirer les espaces (séparateurs de milliers) - incluant les espaces insécables
    cleaned = cleaned.replace(' ', '').replace('\xa0', '')
    
    # Remplacer la virgule par un point (séparateur décimal)
    cleaned = cleaned.replace(',', '.')
    
    try:
        return Decimal(cleaned)
    except (ValueError, TypeError, Exception):
        return Decimal('0')


def format_fcfa_short(amount):
    """
    Formate un montant FCFA de manière compacte (K pour milliers, M pour millions).
    
    Args:
        amount: Montant à formater
    
    Returns:
        str: Montant formaté de manière compacte
    
    Examples:
        >>> format_fcfa_short(1500)
        '1,5 K FCFA'
        >>> format_fcfa_short(1500000)
        '1,5 M FCFA'
    """
    if amount is None:
        return "0 FCFA"
    
    amount = float(amount)
    
    if amount >= 1_000_000_000:
        return f"{amount / 1_000_000_000:,.1f} Mrd FCFA".replace('.', ',')
    elif amount >= 1_000_000:
        return f"{amount / 1_000_000:,.1f} M FCFA".replace('.', ',')
    elif amount >= 1_000:
        return f"{amount / 1_000:,.1f} K FCFA".replace('.', ',')
    else:
        return format_fcfa(amount)
