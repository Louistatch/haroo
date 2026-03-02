"""
Modèles pour la conformité réglementaire
Exigences: 45.1, 45.2, 45.3, 45.4, 45.5, 45.6, 33.6
"""
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class CGUAcceptance(TimeStampedModel):
    """
    Enregistrement de l'acceptation des CGU par les utilisateurs
    Exigence: 45.3
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cgu_acceptances',
        verbose_name="Utilisateur"
    )
    version_cgu = models.CharField(
        max_length=20,
        verbose_name="Version des CGU",
        help_text="Version des CGU acceptées (ex: 1.0, 1.1)"
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="Adresse IP",
        help_text="Adresse IP lors de l'acceptation"
    )
    user_agent = models.TextField(
        verbose_name="User Agent",
        help_text="User agent du navigateur"
    )
    accepted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'acceptation"
    )

    class Meta:
        verbose_name = "Acceptation CGU"
        verbose_name_plural = "Acceptations CGU"
        ordering = ['-accepted_at']
        indexes = [
            models.Index(fields=['user', 'accepted_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - CGU v{self.version_cgu} - {self.accepted_at}"


class ElectronicReceipt(TimeStampedModel):
    """
    Reçus électroniques pour les transactions
    Exigence: 45.5
    """
    transaction = models.OneToOneField(
        'payments.Transaction',
        on_delete=models.PROTECT,
        related_name='receipt',
        verbose_name="Transaction"
    )
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de reçu",
        help_text="Numéro unique du reçu (ex: REC-2024-00001)"
    )
    buyer_name = models.CharField(
        max_length=200,
        verbose_name="Nom de l'acheteur"
    )
    buyer_phone = models.CharField(
        max_length=15,
        verbose_name="Téléphone de l'acheteur"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Description de la transaction"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Montant (FCFA)"
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Montant TVA (FCFA)"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Montant total (FCFA)"
    )
    issued_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'émission"
    )
    pdf_file = models.FileField(
        upload_to='receipts/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Fichier PDF"
    )

    class Meta:
        verbose_name = "Reçu électronique"
        verbose_name_plural = "Reçus électroniques"
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['receipt_number']),
            models.Index(fields=['issued_at']),
        ]

    def __str__(self):
        return f"{self.receipt_number} - {self.buyer_name} - {self.total_amount} FCFA"


class DataRetentionPolicy(models.Model):
    """
    Politique de rétention des données
    Exigence: 45.6
    """
    RETENTION_TYPE_CHOICES = [
        ('TRANSACTION', 'Données de transaction'),
        ('USER_DATA', 'Données utilisateur'),
        ('LOGS', 'Logs système'),
        ('DOCUMENTS', 'Documents'),
    ]
    
    data_type = models.CharField(
        max_length=20,
        choices=RETENTION_TYPE_CHOICES,
        unique=True,
        verbose_name="Type de données"
    )
    retention_period_days = models.IntegerField(
        verbose_name="Période de rétention (jours)",
        help_text="Nombre de jours de conservation des données"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Description de la politique de rétention"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )

    class Meta:
        verbose_name = "Politique de rétention"
        verbose_name_plural = "Politiques de rétention"
        ordering = ['data_type']

    def __str__(self):
        return f"{self.get_data_type_display()} - {self.retention_period_days} jours"


class AccountDeletionRequest(TimeStampedModel):
    """
    Demandes de suppression de compte
    Exigence: 45.4
    """
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('PROCESSING', 'En cours de traitement'),
        ('COMPLETED', 'Terminée'),
        ('CANCELLED', 'Annulée'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deletion_requests',
        verbose_name="Utilisateur"
    )
    reason = models.TextField(
        blank=True,
        verbose_name="Raison",
        help_text="Raison de la suppression (optionnel)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Statut"
    )
    requested_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de demande"
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de traitement"
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_deletions',
        verbose_name="Traité par"
    )
    data_export_file = models.FileField(
        upload_to='data_exports/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Fichier d'export des données"
    )

    class Meta:
        verbose_name = "Demande de suppression"
        verbose_name_plural = "Demandes de suppression"
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['requested_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()} - {self.requested_at}"
