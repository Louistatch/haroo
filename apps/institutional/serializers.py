"""
Serializers pour le dashboard institutionnel
"""
from rest_framework import serializers


class RegionSerializer(serializers.Serializer):
    """Serializer pour les informations de région"""
    id = serializers.IntegerField()
    nom = serializers.CharField()
    code = serializers.CharField()


class PrefectureSerializer(serializers.Serializer):
    """Serializer pour les informations de préfecture"""
    id = serializers.IntegerField()
    nom = serializers.CharField()
    code = serializers.CharField()
    region = RegionSerializer()


class EmploisSerializer(serializers.Serializer):
    """Serializer pour les statistiques d'emplois"""
    total = serializers.IntegerField()
    agronomes = serializers.IntegerField()
    ouvriers = serializers.IntegerField()


class TransactionsSerializer(serializers.Serializer):
    """Serializer pour les statistiques de transactions"""
    volume = serializers.IntegerField()
    valeur_totale_fcfa = serializers.FloatField()
    commission_plateforme_fcfa = serializers.FloatField()


class AggregatedStatisticsSerializer(serializers.Serializer):
    """Serializer pour les statistiques agrégées"""
    nombre_exploitations = serializers.IntegerField()
    superficie_totale_hectares = serializers.FloatField()
    emplois_crees = EmploisSerializer()
    transactions = TransactionsSerializer()
    region = RegionSerializer(required=False)


class PrefectureStatisticsSerializer(serializers.Serializer):
    """Serializer pour les statistiques par préfecture"""
    prefecture = PrefectureSerializer()
    nombre_exploitations = serializers.IntegerField()
    superficie_totale_hectares = serializers.FloatField()
    nombre_agronomes = serializers.IntegerField()


class TransactionBreakdownSerializer(serializers.Serializer):
    """Serializer pour la répartition des transactions"""
    type = serializers.CharField()
    nombre_transactions = serializers.IntegerField()
    montant_total_fcfa = serializers.FloatField()
    commission_totale_fcfa = serializers.FloatField()


class PeriodeSerializer(serializers.Serializer):
    """Serializer pour une période"""
    annee = serializers.IntegerField()
    mois = serializers.IntegerField()
    mois_nom = serializers.CharField()
    debut = serializers.DateTimeField()
    fin = serializers.DateTimeField()


class MonthlyTrendSerializer(serializers.Serializer):
    """Serializer pour les tendances mensuelles"""
    periode = PeriodeSerializer()
    nombre_exploitations = serializers.IntegerField()
    superficie_totale_hectares = serializers.FloatField()
    emplois_crees = EmploisSerializer()
    transactions = TransactionsSerializer()


class DashboardQuerySerializer(serializers.Serializer):
    """Serializer pour les paramètres de requête du dashboard"""
    region = serializers.IntegerField(required=False, help_text="ID de la région pour filtrer")
    start_date = serializers.DateTimeField(required=False, help_text="Date de début (format ISO 8601)")
    end_date = serializers.DateTimeField(required=False, help_text="Date de fin (format ISO 8601)")
    months = serializers.IntegerField(required=False, default=12, min_value=1, max_value=24, 
                                      help_text="Nombre de mois pour les tendances (1-24)")
