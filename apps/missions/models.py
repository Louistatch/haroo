"""
Modèles pour la gestion des missions d'agronomes
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
from apps.payments.models import Transaction


class Mission(TimeStampedModel):
    """
    Modèle pour les missions d'agronomes
    """
    STATUT_CHOICES = [
        ('DEMANDE', 'Demande Envoyée'),
        ('ACCEPTEE', 'Acceptée'),
        ('REFUSEE', 'Refusée'),
        ('EN_COURS', 'En Cours'),
        ('TERMINEE', 'Terminée'),
        ('ANNULEE', 'Annulée'),
    ]
    
    exploitant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='missions_creees',
        verbose_name="Exploitant"
    )
    agronome = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='missions_recues',
        verbose_name="Agronome"
    )
    description = models.TextField(verbose_name="Description")
    budget_propose = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Budget proposé (FCFA)"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='DEMANDE',
        verbose_name="Statut"
    )
    date_debut = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de début"
    )
    date_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de fin"
    )
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Transaction"
    )
    
    class Meta:
        verbose_name = "Mission"
        verbose_name_plural = "Missions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['exploitant', 'statut']),
            models.Index(fields=['agronome', 'statut']),
        ]
    
    def __str__(self):
        return f"Mission #{self.id} - {self.exploitant.get_full_name()} → {self.agronome.get_full_name()}"
    
    def clean(self):
        """Validation du modèle"""
        super().clean()
        
        # Vérifier que l'exploitant est bien un exploitant vérifié
        if not hasattr(self.exploitant, 'exploitant_profile'):
            raise ValidationError("L'utilisateur doit avoir un profil d'exploitant")
        
        if self.exploitant.exploitant_profile.statut_verification != 'VERIFIE':
            raise ValidationError("L'exploitant doit être vérifié pour créer une mission")
        
        # Vérifier que l'agronome est bien un agronome validé
        if not hasattr(self.agronome, 'agronome_profile'):
            raise ValidationError("L'utilisateur doit avoir un profil d'agronome")
        
        if self.agronome.agronome_profile.statut_validation != 'VALIDE':
            raise ValidationError("L'agronome doit être validé pour recevoir une mission")
        
        # Vérifier que les dates sont cohérentes
        if self.date_debut and self.date_fin and self.date_debut > self.date_fin:
            raise ValidationError("La date de début doit être antérieure à la date de fin")
        
        # Vérifier que le budget est positif
        if self.budget_propose <= 0:
            raise ValidationError("Le budget proposé doit être positif")
