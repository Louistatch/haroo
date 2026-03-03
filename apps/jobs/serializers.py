from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OffreEmploiSaisonnier, ContratSaisonnier, HeuresTravaillees

User = get_user_model()


class OffreListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des offres d'emploi"""
    exploitant_nom = serializers.CharField(source='exploitant.get_full_name', read_only=True)
    canton_nom = serializers.CharField(source='canton.nom', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)

    class Meta:
        model = OffreEmploiSaisonnier
        fields = [
            'id', 'type_travail', 'description', 'canton_nom',
            'date_debut', 'date_fin', 'salaire_horaire', 'nombre_postes',
            'postes_pourvus', 'statut', 'statut_display', 'exploitant_nom', 'created_at'
        ]


class OffreDetailSerializer(serializers.ModelSerializer):
    """Serializer pour le détail d'une offre d'emploi"""
    exploitant_nom = serializers.CharField(source='exploitant.get_full_name', read_only=True)
    canton_nom = serializers.CharField(source='canton.nom', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)

    class Meta:
        model = OffreEmploiSaisonnier
        fields = [
            'id', 'exploitant', 'exploitant_nom', 'type_travail', 'description',
            'canton', 'canton_nom', 'date_debut', 'date_fin', 'salaire_horaire',
            'nombre_postes', 'postes_pourvus', 'statut', 'statut_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'exploitant', 'postes_pourvus', 'created_at', 'updated_at']


class OffreCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'une offre d'emploi"""
    class Meta:
        model = OffreEmploiSaisonnier
        fields = [
            'type_travail', 'description', 'canton', 'date_debut',
            'date_fin', 'salaire_horaire', 'nombre_postes'
        ]

    def validate_salaire_horaire(self, value):
        from django.conf import settings
        min_salaire = getattr(settings, 'SALAIRE_MINIMUM_HORAIRE', 500)
        if value < min_salaire:
            raise serializers.ValidationError(f"Le salaire horaire doit être au moins de {min_salaire} FCFA")
        return value

    def validate(self, data):
        if data['date_debut'] > data['date_fin']:
            raise serializers.ValidationError("La date de début doit être antérieure à la date de fin")
        return data


class ContratSerializer(serializers.ModelSerializer):
    """Serializer pour les contrats saisonniers"""
    ouvrier_nom = serializers.CharField(source='ouvrier.get_full_name', read_only=True)
    exploitant_nom = serializers.CharField(source='exploitant.get_full_name', read_only=True)
    type_travail = serializers.CharField(source='offre.type_travail', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)

    class Meta:
        model = ContratSaisonnier
        fields = [
            'id', 'offre', 'type_travail', 'ouvrier', 'ouvrier_nom',
            'exploitant', 'exploitant_nom', 'date_debut', 'date_fin',
            'salaire_horaire', 'statut', 'statut_display', 'created_at'
        ]
        read_only_fields = ['id', 'exploitant', 'ouvrier', 'salaire_horaire', 'statut', 'created_at']


class HeuresSerializer(serializers.ModelSerializer):
    """Serializer pour les heures travaillées"""
    class Meta:
        model = HeuresTravaillees
        fields = ['id', 'contrat', 'date', 'heures', 'statut_validation', 'montant_calcule', 'created_at']
        read_only_fields = ['id', 'statut_validation', 'montant_calcule', 'created_at']

    def validate_heures(self, value):
        if value <= 0:
            raise serializers.ValidationError("Les heures doivent être supérieures à zéro")
        if value > 24:
            raise serializers.ValidationError("Les heures ne peuvent pas dépasser 24 heures par jour")
        return value
