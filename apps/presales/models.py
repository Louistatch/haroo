from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from apps.core.models import TimeStampedModel
from apps.payments.models import Transaction


class PreventeAgricole(TimeStampedModel):
    """
    Modèle pour les préventes agricoles
    """
    STATUT_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('ENGAGEE', 'Engagée'),
        ('LIVREE', 'Livrée'),
        ('ANNULEE', 'Annulée'),
    ]

    exploitant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preventes',
        verbose_name="Exploitant"
    )
    culture = models.CharField(max_length=100, verbose_name="Culture")
    quantite_estimee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Quantité estimée (tonnes)"
    )
    date_recolte_prevue = models.DateField(verbose_name="Date de récolte prévue")
    prix_par_tonne = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Prix par tonne (FCFA)"
    )
    canton_production = models.ForeignKey(
        'locations.Canton', 
        on_delete=models.PROTECT,
        verbose_name="Canton de production"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='DISPONIBLE',
        verbose_name="Statut"
    )

    @property
    def montant_total(self):
        return self.quantite_estimee * self.prix_par_tonne

    class Meta:
        verbose_name = "Prévente Agricole"
        verbose_name_plural = "Préventes Agricoles"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.culture} - {self.exploitant.get_full_name()} ({self.quantite_estimee}t)"

    def clean(self):
        super().clean()
        if self.date_recolte_prevue:
            if self.date_recolte_prevue < date.today() + timedelta(days=30):
                raise ValidationError(
                    {'date_recolte_prevue': "La date de récolte prévue doit être au moins 30 jours dans le futur."}
                )


class EngagementPrevente(TimeStampedModel):
    """
    Modèle pour l'engagement d'un acheteur sur une prévente
    """
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En Attente'),
        ('ACOMPTE_PAYE', 'Acompte Payé'),
        ('LIVRAISON_CONFIRMEE', 'Livraison Confirmée'),
        ('PAIEMENT_COMPLET', 'Paiement Complet'),
        ('ANNULE', 'Annulé'),
    ]

    prevente = models.ForeignKey(
        PreventeAgricole, 
        related_name='engagements', 
        on_delete=models.PROTECT,
        verbose_name="Prévente"
    )
    acheteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='engagements_acheteur',
        on_delete=models.CASCADE,
        verbose_name="Acheteur"
    )
    quantite_engagee = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Quantité engagée"
    )
    montant_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Montant total"
    )
    acompte_20 = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Acompte (20%)"
    )
    transaction_acompte = models.ForeignKey(
        Transaction, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        verbose_name="Transaction d'acompte"
    )
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='EN_ATTENTE',
        verbose_name="Statut"
    )
    date_livraison = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Date de livraison"
    )

    class Meta:
        verbose_name = "Engagement de Prévente"
        verbose_name_plural = "Engagements de Prévente"
        ordering = ['-created_at']

    def __str__(self):
        return f"Engagement {self.acheteur.get_full_name()} - {self.prevente.culture}"
