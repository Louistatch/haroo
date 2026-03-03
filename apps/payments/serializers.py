"""
Serializers pour l'API de paiements
"""
from rest_framework import serializers
from decimal import Decimal

from .models import Transaction
from apps.core.fields import FCFAField, FCFADecimalField


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Transaction
    """
    utilisateur_nom = serializers.CharField(
        source='utilisateur.get_full_name',
        read_only=True
    )
    type_transaction_display = serializers.CharField(
        source='get_type_transaction_display',
        read_only=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )
    # Montants formatés en FCFA
    montant_display = FCFAField(source='montant', read_only=True, decimal_places=2)
    commission_display = FCFAField(source='commission_plateforme', read_only=True, decimal_places=2)
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'utilisateur',
            'utilisateur_nom',
            'type_transaction',
            'type_transaction_display',
            'montant',
            'montant_display',
            'commission_plateforme',
            'commission_display',
            'statut',
            'statut_display',
            'fedapay_transaction_id',
            'reference_externe',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'utilisateur',
            'commission_plateforme',
            'statut',
            'fedapay_transaction_id',
            'created_at',
            'updated_at'
        ]


class InitiatePaymentSerializer(serializers.Serializer):
    """
    Serializer pour l'initialisation d'un paiement
    """
    type_transaction = serializers.ChoiceField(
        choices=Transaction.TYPE_CHOICES,
        required=True,
        help_text="Type de transaction"
    )
    montant = FCFADecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('100.00'),  # Montant minimum de 100 FCFA
        required=True,
        help_text="Montant en FCFA (minimum 100). Accepte les formats: 1000, 1 000, 1000,50"
    )
    reference_externe = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Référence externe (ID document, mission, etc.)"
    )
    description = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Description du paiement"
    )
    callback_url = serializers.URLField(
        required=False,
        help_text="URL de retour après paiement (optionnel)"
    )
    
    def validate_montant(self, value):
        """Valider que le montant est positif et raisonnable"""
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être positif")
        
        if value > Decimal('10000000.00'):  # Maximum 10 millions FCFA
            raise serializers.ValidationError(
                "Le montant ne peut pas dépasser 10 000 000 FCFA"
            )
        
        return value


class PaymentResponseSerializer(serializers.Serializer):
    """
    Serializer pour la réponse d'initialisation de paiement
    """
    success = serializers.BooleanField()
    transaction_id = serializers.UUIDField()
    fedapay_transaction_id = serializers.CharField()
    payment_url = serializers.URLField()
    token = serializers.CharField()
    message = serializers.CharField(required=False)


class TransactionHistorySerializer(serializers.ModelSerializer):
    """
    Serializer pour l'historique des transactions
    """
    type_transaction_display = serializers.CharField(
        source='get_type_transaction_display',
        read_only=True
    )
    statut_display = serializers.CharField(
        source='get_statut_display',
        read_only=True
    )
    # Montants formatés en FCFA pour l'affichage
    montant_display = FCFAField(source='montant', read_only=True, decimal_places=2)
    commission_display = FCFAField(source='commission_plateforme', read_only=True, decimal_places=2)
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'type_transaction',
            'type_transaction_display',
            'montant',
            'montant_display',
            'commission_plateforme',
            'commission_display',
            'statut',
            'statut_display',
            'reference_externe',
            'created_at'
        ]
        read_only_fields = fields


class WebhookPayloadSerializer(serializers.Serializer):
    """
    Serializer pour valider les données du webhook FedaPay.
    FedaPay envoie 'name' pour le type d'événement (pas 'event').
    """
    entity = serializers.DictField(required=True)
    name   = serializers.CharField(required=False, allow_blank=True)
    event  = serializers.CharField(required=False, allow_blank=True)

    SUPPORTED_EVENTS = {
        'transaction.approved',
        'transaction.canceled',
        'transaction.declined',
        'transaction.failed',
        'transaction.transferred',
    }

    def validate(self, data):
        event_name = data.get('name') or data.get('event', '')
        if not event_name:
            raise serializers.ValidationError("Champ 'name' ou 'event' requis")
        data['event'] = event_name
        return data
