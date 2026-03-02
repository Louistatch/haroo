"""
Modèles pour la gestion des paiements via Fedapay
"""
import uuid
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class Transaction(TimeStampedModel):
    """
    Modèle pour les transactions de paiement
    """
    TYPE_CHOICES = [
        ('ACHAT_DOCUMENT', 'Achat Document'),
        ('RECRUTEMENT_AGRONOME', 'Recrutement Agronome'),
        ('PREVENTE', 'Prévente Agricole'),
        ('TRANSPORT', 'Transport'),
        ('ABONNEMENT', 'Abonnement Premium'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'En Attente'),
        ('SUCCESS', 'Réussie'),
        ('FAILED', 'Échouée'),
        ('REFUNDED', 'Remboursée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="Utilisateur"
    )
    type_transaction = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        verbose_name="Type"
    )
    montant = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Montant (FCFA)"
    )
    commission_plateforme = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Commission"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Statut"
    )
    fedapay_transaction_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        verbose_name="ID Fedapay"
    )
    reference_externe = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Référence externe"
    )

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['utilisateur', 'created_at']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"{self.get_type_transaction_display()} - {self.montant} FCFA ({self.get_statut_display()})"


class EscrowAccount(TimeStampedModel):
    """
    Compte de séquestre pour missions et préventes
    Retient les paiements jusqu'à confirmation de fin de service
    """
    STATUT_CHOICES = [
        ('BLOQUE', 'Bloqué'),
        ('LIBERE', 'Libéré'),
        ('REMBOURSE', 'Remboursé'),
    ]
    
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.PROTECT,
        verbose_name="Transaction"
    )
    montant_bloque = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Montant bloqué (FCFA)"
    )
    beneficiaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='escrow_beneficiaire',
        verbose_name="Bénéficiaire"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='BLOQUE',
        verbose_name="Statut"
    )
    date_liberation_prevue = models.DateTimeField(
        verbose_name="Date de libération prévue"
    )
    date_liberation_effective = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de libération effective"
    )
    
    class Meta:
        verbose_name = "Compte Escrow"
        verbose_name_plural = "Comptes Escrow"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['statut', 'date_liberation_prevue']),
            models.Index(fields=['beneficiaire', 'statut']),
        ]
    
    def __str__(self):
        return f"Escrow #{self.id} - {self.montant_bloque} FCFA ({self.get_statut_display()})"
