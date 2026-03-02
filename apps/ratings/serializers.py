"""
Serializers pour le système de notation
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notation, SignalementNotation
from apps.missions.models import Mission

User = get_user_model()


class NotationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de notations
    Exigences: 27.1, 27.2
    """
    class Meta:
        model = Notation
        fields = ['note_valeur', 'commentaire', 'mission']
        extra_kwargs = {
            'note_valeur': {
                'min_value': 1,
                'max_value': 5,
                'error_messages': {
                    'min_value': 'La note doit être entre 1 et 5 étoiles',
                    'max_value': 'La note doit être entre 1 et 5 étoiles',
                }
            },
            'commentaire': {
                'min_length': 20,
                'error_messages': {
                    'min_length': 'Le commentaire doit contenir au minimum 20 caractères',
                }
            }
        }
    
    def validate_mission(self, value):
        """Valider que la mission existe et est terminée"""
        if not value:
            raise serializers.ValidationError("Une mission doit être spécifiée")
        
        if value.statut != 'TERMINEE':
            raise serializers.ValidationError(
                "La notation n'est autorisée qu'après la fin de la mission"
            )
        
        return value
    
    def validate(self, attrs):
        """Validation globale"""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Utilisateur non authentifié")
        
        mission = attrs.get('mission')
        
        # Vérifier que l'utilisateur était partie prenante de la mission
        if request.user not in [mission.exploitant, mission.agronome]:
            raise serializers.ValidationError(
                "Seuls les participants à la mission peuvent la noter"
            )
        
        # Déterminer qui doit être noté
        if request.user == mission.exploitant:
            attrs['note'] = mission.agronome
        else:
            attrs['note'] = mission.exploitant
        
        attrs['notateur'] = request.user
        
        # Vérifier qu'une notation n'existe pas déjà
        if Notation.objects.filter(notateur=request.user, mission=mission).exists():
            raise serializers.ValidationError(
                "Vous avez déjà noté cette mission"
            )
        
        return attrs


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer basique pour les informations utilisateur"""
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number']


class NotationListSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'affichage des notations
    Exigence: 27.4
    """
    notateur = UserBasicSerializer(read_only=True)
    note = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Notation
        fields = [
            'id',
            'notateur',
            'note',
            'note_valeur',
            'commentaire',
            'mission',
            'statut',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields


class NotationDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une notation"""
    notateur = UserBasicSerializer(read_only=True)
    note = UserBasicSerializer(read_only=True)
    nombre_signalements = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Notation
        fields = [
            'id',
            'notateur',
            'note',
            'note_valeur',
            'commentaire',
            'mission',
            'statut',
            'nombre_signalements',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields


class SignalementNotationSerializer(serializers.ModelSerializer):
    """
    Serializer pour signaler une notation
    Exigence: 27.5
    """
    class Meta:
        model = SignalementNotation
        fields = ['notation', 'motif', 'description']
    
    def validate_notation(self, value):
        """Valider que la notation existe et est publiée"""
        if value.statut == 'REJETE':
            raise serializers.ValidationError("Cette notation a déjà été rejetée")
        
        return value
    
    def validate(self, attrs):
        """Validation globale"""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Utilisateur non authentifié")
        
        notation = attrs.get('notation')
        
        # Vérifier qu'un signalement n'existe pas déjà
        if SignalementNotation.objects.filter(
            notation=notation,
            signaleur=request.user
        ).exists():
            raise serializers.ValidationError(
                "Vous avez déjà signalé cette notation"
            )
        
        attrs['signaleur'] = request.user
        
        return attrs
