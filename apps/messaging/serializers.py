from rest_framework import serializers
from .models import Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email']

class MessageSerializer(serializers.ModelSerializer):
    expediteur_nom = serializers.CharField(source='expediteur.get_full_name', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'expediteur', 'expediteur_nom', 'contenu', 'lu', 'date_lecture', 'signale', 'created_at']
        read_only_fields = ['expediteur', 'lu', 'date_lecture', 'signale']

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['contenu']

class ConversationSerializer(serializers.ModelSerializer):
    participant_1 = UserShortSerializer(read_only=True)
    participant_2 = UserShortSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    interlocuteur = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'participant_1', 'participant_2', 'type_relation', 
            'reference_id', 'derniere_activite', 'last_message', 
            'unread_count', 'interlocuteur', 'created_at'
        ]

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(lu=False).exclude(expediteur=request.user).count()
        return 0

    def get_interlocuteur(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj.participant_1 == request.user:
                return UserShortSerializer(obj.participant_2).data
            return UserShortSerializer(obj.participant_1).data
        return None
