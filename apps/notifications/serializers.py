from rest_framework import serializers
from .models import Notification, PreferenceNotification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('utilisateur', 'created_at', 'updated_at')

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreferenceNotification
        fields = '__all__'
        read_only_fields = ('user',)
