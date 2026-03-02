"""
Serializers pour la gestion des missions
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Mission

User = get_user_model()


class MissionCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'une mission"""
    
    class Meta:
        model = Mission
        fields = ['agronome', 'description', 'budget_propose', 'date_debut', 'date_fin']
    
    def validate_agronome(self, value):
        """Valider que l'agronome est validé"""
        if not hasattr(value, 'agronome_profile'):
            raise serializers.ValidationError("L'utilisateur doit avoir un profil d'agronome")
        
        if value.agronome_profile.statut_validation != 'VALIDE':
            raise serializers.ValidationError("L'agronome doit être validé")
        
        return value
    
    def validate_budget_propose(self, value):
        """Valider que le budget est positif"""
        if value <= 0:
            raise serializers.ValidationError("Le budget proposé doit être positif")
        return value
    
    def validate(self, data):
        """Validation globale"""
        # Vérifier que les dates sont cohérentes
        if data.get('date_debut') and data.get('date_fin'):
            if data['date_debut'] > data['date_fin']:
                raise serializers.ValidationError({
                    'date_fin': "La date de fin doit être postérieure à la date de début"
                })
        
        return data
    
    def create(self, validated_data):
        """Créer une mission avec l'exploitant du contexte"""
        validated_data['exploitant'] = self.context['request'].user
        validated_data['statut'] = 'DEMANDE'
        return super().create(validated_data)


class MissionDetailSerializer(serializers.ModelSerializer):
    """Serializer pour les détails d'une mission"""
    exploitant_nom = serializers.CharField(source='exploitant.get_full_name', read_only=True)
    agronome_nom = serializers.CharField(source='agronome.get_full_name', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    class Meta:
        model = Mission
        fields = [
            'id', 'exploitant', 'exploitant_nom', 'agronome', 'agronome_nom',
            'description', 'budget_propose', 'statut', 'statut_display',
            'date_debut', 'date_fin', 'transaction', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'exploitant', 'statut', 'transaction', 'created_at', 'updated_at']


class MissionListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des missions"""
    exploitant_nom = serializers.CharField(source='exploitant.get_full_name', read_only=True)
    agronome_nom = serializers.CharField(source='agronome.get_full_name', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    class Meta:
        model = Mission
        fields = [
            'id', 'exploitant_nom', 'agronome_nom', 'description',
            'budget_propose', 'statut', 'statut_display', 'created_at'
        ]


class MissionAcceptSerializer(serializers.Serializer):
    """Serializer pour l'acceptation d'une mission"""
    pass  # Pas de champs supplémentaires nécessaires


class MissionCompleteSerializer(serializers.Serializer):
    """Serializer pour la complétion d'une mission"""
    pass  # Pas de champs supplémentaires nécessaires
