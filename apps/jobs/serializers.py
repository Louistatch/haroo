from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    OffreEmploiSaisonnier, ContratSaisonnier, HeuresTravaillees,
    AnnonceCollective, ParticipationAnnonce, AnnonceOuvrier, SEUIL_HECTARES
)
from apps.locations.models import Canton

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
            'postes_pourvus', 'statut', 'statut_display', 'exploitant_nom',
            'est_collective', 'created_at'
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
            'nombre_postes', 'postes_pourvus', 'statut', 'statut_display',
            'est_collective', 'created_at', 'updated_at'
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


class ParticipationSerializer(serializers.ModelSerializer):
    exploitant_nom = serializers.CharField(source='exploitant.get_full_name', read_only=True)

    class Meta:
        model = ParticipationAnnonce
        fields = ['id', 'annonce', 'exploitant', 'exploitant_nom', 'superficie_apportee', 'created_at']
        read_only_fields = ['id', 'exploitant', 'created_at']


class AnnonceCollectiveListSerializer(serializers.ModelSerializer):
    createur_nom = serializers.CharField(source='createur.get_full_name', read_only=True)
    canton_nom = serializers.CharField(source='canton.nom', read_only=True)
    nb_participants = serializers.SerializerMethodField()
    progression = serializers.SerializerMethodField()

    class Meta:
        model = AnnonceCollective
        fields = [
            'id', 'createur_nom', 'type_travail', 'description',
            'canton_nom', 'date_debut', 'date_fin', 'salaire_horaire',
            'nombre_postes', 'superficie_cumulee', 'seuil_hectares',
            'date_expiration', 'statut', 'nb_participants', 'progression',
            'created_at'
        ]

    def get_nb_participants(self, obj):
        return obj.participations.count()

    def get_progression(self, obj):
        if obj.seuil_hectares <= 0:
            return 100
        return round(float(obj.superficie_cumulee) / float(obj.seuil_hectares) * 100, 1)


class AnnonceCollectiveDetailSerializer(AnnonceCollectiveListSerializer):
    participations = ParticipationSerializer(many=True, read_only=True)

    class Meta(AnnonceCollectiveListSerializer.Meta):
        fields = AnnonceCollectiveListSerializer.Meta.fields + ['participations']


class AnnonceCollectiveCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnonceCollective
        fields = [
            'type_travail', 'description', 'canton',
            'date_debut', 'date_fin', 'salaire_horaire', 'nombre_postes'
        ]

    def validate(self, data):
        if data['date_debut'] > data['date_fin']:
            raise serializers.ValidationError("La date de début doit être antérieure à la date de fin")
        return data



# ─── Annonces d'ouvriers ───

class AnnonceOuvrierListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des annonces d'ouvriers"""
    ouvrier_nom = serializers.CharField(source='ouvrier.get_full_name', read_only=True)
    cantons_noms = serializers.SerializerMethodField()
    progression = serializers.ReadOnlyField()

    class Meta:
        model = AnnonceOuvrier
        fields = [
            'id', 'ouvrier', 'ouvrier_nom', 'titre', 'description',
            'competences', 'cantons_noms', 'tarif_horaire_min',
            'date_disponibilite_debut', 'date_disponibilite_fin',
            'statut', 'type_annonce', 'equipe_complete', 'nb_membres_actuels',
            'progression', 'date_expiration', 'created_at'
        ]

    def get_cantons_noms(self, obj):
        return [c.nom for c in obj.cantons_disponibles.all()]


class AnnonceOuvrierDetailSerializer(AnnonceOuvrierListSerializer):
    """Serializer pour le détail d'une annonce d'ouvrier"""
    membres_equipe = serializers.JSONField(read_only=True)
    membres_rejoints = serializers.JSONField(read_only=True)
    
    class Meta(AnnonceOuvrierListSerializer.Meta):
        fields = AnnonceOuvrierListSerializer.Meta.fields + ['membres_equipe', 'membres_rejoints']


class AnnonceOuvrierCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'une annonce d'ouvrier"""
    cantons_disponibles = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Canton.objects.all()
    )
    membres_equipe = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = AnnonceOuvrier
        fields = [
            'titre', 'description', 'competences', 'cantons_disponibles',
            'tarif_horaire_min', 'date_disponibilite_debut',
            'date_disponibilite_fin', 'type_annonce', 'equipe_complete',
            'membres_equipe'
        ]

    def validate(self, data):
        if data.get('date_disponibilite_fin'):
            if data['date_disponibilite_debut'] > data['date_disponibilite_fin']:
                raise serializers.ValidationError(
                    "La date de début doit être antérieure à la date de fin"
                )
        
        # Validation pour annonce individuelle
        if data.get('type_annonce') == 'INDIVIDUELLE' and data.get('equipe_complete'):
            membres = data.get('membres_equipe', [])
            if len(membres) != 7:
                raise serializers.ValidationError(
                    "Vous devez fournir exactement 7 membres pour compléter l'équipe"
                )
            # Vérifier que chaque membre a nom, prénom, téléphone
            for i, membre in enumerate(membres):
                if not all(k in membre for k in ['nom', 'prenom', 'telephone']):
                    raise serializers.ValidationError(
                        f"Le membre {i+1} doit avoir nom, prénom et téléphone"
                    )
        
        return data
