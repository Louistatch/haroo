"""
Champs personnalisés pour les serializers DRF
"""

from decimal import Decimal
from rest_framework import serializers
from apps.core.currency import format_fcfa, parse_fcfa


class FCFAField(serializers.DecimalField):
    """
    Champ de serializer pour les montants en FCFA.
    
    - En lecture: Formate le montant avec le symbole FCFA
    - En écriture: Parse les montants avec ou sans symbole FCFA
    
    Usage:
        class TransactionSerializer(serializers.ModelSerializer):
            montant = FCFAField(max_digits=12, decimal_places=2)
    """
    
    def __init__(self, *args, **kwargs):
        # Par défaut, pas de décimales pour FCFA
        kwargs.setdefault('decimal_places', 0)
        kwargs.setdefault('max_digits', 12)
        self.format_output = kwargs.pop('format_output', True)
        super().__init__(*args, **kwargs)
    
    def to_representation(self, value):
        """Formate le montant en FCFA pour la sortie"""
        if value is None:
            return None
        
        if self.format_output:
            return format_fcfa(value, use_symbol=True, decimal_places=self.decimal_places)
        else:
            # Retourner le nombre formaté sans symbole
            return super().to_representation(value)
    
    def to_internal_value(self, data):
        """Parse le montant FCFA pour l'entrée"""
        if isinstance(data, str):
            # Si c'est une chaîne, parser le format FCFA
            data = parse_fcfa(data)
        
        return super().to_internal_value(data)


class FCFADecimalField(serializers.DecimalField):
    """
    Champ de serializer pour les montants en FCFA avec décimales.
    Retourne uniquement le nombre (pas de symbole) pour faciliter les calculs côté client.
    
    Usage:
        class PrixSerializer(serializers.ModelSerializer):
            prix_unitaire = FCFADecimalField(max_digits=10, decimal_places=2)
    """
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('decimal_places', 2)
        kwargs.setdefault('max_digits', 12)
        super().__init__(*args, **kwargs)
    
    def to_representation(self, value):
        """Retourne le nombre avec virgule comme séparateur décimal"""
        if value is None:
            return None
        
        # Formater avec la locale française (virgule décimale)
        result = super().to_representation(value)
        if isinstance(result, str):
            # Remplacer le point par une virgule
            result = result.replace('.', ',')
        return result
    
    def to_internal_value(self, data):
        """Parse le montant avec virgule ou point"""
        if isinstance(data, str):
            # Accepter virgule ou point comme séparateur décimal
            data = data.replace(',', '.')
        
        return super().to_internal_value(data)
