"""
Serializers pour la conformité réglementaire
"""
from rest_framework import serializers
from .models import (
    CGUAcceptance,
    ElectronicReceipt,
    AccountDeletionRequest,
    DataRetentionPolicy
)


class CGUAcceptanceSerializer(serializers.ModelSerializer):
    """Serializer pour l'acceptation des CGU"""
    
    class Meta:
        model = CGUAcceptance
        fields = [
            'id',
            'version_cgu',
            'accepted_at',
            'ip_address'
        ]
        read_only_fields = ['id', 'accepted_at', 'ip_address']


class AcceptCGUSerializer(serializers.Serializer):
    """Serializer pour accepter les CGU"""
    version_cgu = serializers.CharField(required=False)
    accepted = serializers.BooleanField(required=True)
    
    def validate_accepted(self, value):
        if not value:
            raise serializers.ValidationError(
                "Vous devez accepter les conditions générales d'utilisation"
            )
        return value


class ElectronicReceiptSerializer(serializers.ModelSerializer):
    """Serializer pour les reçus électroniques"""
    transaction_id = serializers.UUIDField(source='transaction.id', read_only=True)
    pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ElectronicReceipt
        fields = [
            'id',
            'transaction_id',
            'receipt_number',
            'buyer_name',
            'buyer_phone',
            'description',
            'amount',
            'tax_amount',
            'total_amount',
            'issued_at',
            'pdf_url'
        ]
        read_only_fields = fields
    
    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None


class AccountDeletionRequestSerializer(serializers.ModelSerializer):
    """Serializer pour les demandes de suppression de compte"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    data_export_url = serializers.SerializerMethodField()
    
    class Meta:
        model = AccountDeletionRequest
        fields = [
            'id',
            'user_username',
            'reason',
            'status',
            'requested_at',
            'processed_at',
            'data_export_url'
        ]
        read_only_fields = [
            'id',
            'user_username',
            'status',
            'requested_at',
            'processed_at',
            'data_export_url'
        ]
    
    def get_data_export_url(self, obj):
        if obj.data_export_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.data_export_file.url)
            return obj.data_export_file.url
        return None


class CreateDeletionRequestSerializer(serializers.Serializer):
    """Serializer pour créer une demande de suppression"""
    reason = serializers.CharField(required=False, allow_blank=True)
    confirm = serializers.BooleanField(required=True)
    
    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError(
                "Vous devez confirmer la suppression de votre compte"
            )
        return value


class DataExportSerializer(serializers.Serializer):
    """Serializer pour l'export des données personnelles"""
    format = serializers.ChoiceField(
        choices=['json'],
        default='json',
        required=False
    )


class DataRetentionPolicySerializer(serializers.ModelSerializer):
    """Serializer pour les politiques de rétention"""
    
    class Meta:
        model = DataRetentionPolicy
        fields = [
            'id',
            'data_type',
            'retention_period_days',
            'description',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
