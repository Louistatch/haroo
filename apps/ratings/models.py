"""
Modèles pour le système de notation et avis
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from apps.core.models import TimeStampedModel
from apps.missions.models import Mission


class Notation(TimeStampedModel):
    """
    Modèle pour les notations et avis
    Exigences: 27.1, 27.2
    """
    STATUT_CHOICES = [
        ('PUBLIE', 'Publié'),
        ('SIGNALE', 'Signalé'),
        ('MODERE', 'Modéré'),
        ('REJETE', 'Rejeté'),
    ]
    
    # Utilisateur qui note
    notateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='notations_donnees',
        verbose_name="Notateur"
    )
    
    # Utilisateur noté
    note = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='notations_recues',
        verbose_name="Utilisateur noté"
    )
    
    # Note de 1 à 5 étoiles (Exigence 27.1)
    note_valeur = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note (1-5 étoiles)"
    )
    
    # Commentaire minimum 20 caractères (Exigence 27.2)
    commentaire = models.TextField(
        validators=[MinLengthValidator(20)],
        verbose_name="Commentaire"
    )
    
    # Référence à la mission ou contrat complété
    mission = models.ForeignKey(
        Mission,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='notations',
        verbose_name="Mission"
    )
    
    # TODO: Ajouter contrat_saisonnier quand le modèle sera créé
    # contrat_saisonnier = models.ForeignKey(
    #     'ContratSaisonnier',
    #     on_delete=models.PROTECT,
    #     null=True,
    #     blank=True,
    #     related_name='notations',
    #     verbose_name="Contrat saisonnier"
    # )
    
    # Statut pour modération (Exigence 27.5)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='PUBLIE',
        verbose_name="Statut"
    )
    
    # Nombre de signalements
    nombre_signalements = models.IntegerField(
        default=0,
        verbose_name="Nombre de signalements"
    )
    
    class Meta:
        verbose_name = "Notation"
        verbose_name_plural = "Notations"
        ordering = ['-created_at']  # Tri par date décroissante (Exigence 27.4)
        indexes = [
            models.Index(fields=['note', 'statut']),
            models.Index(fields=['notateur']),
            models.Index(fields=['mission']),
            models.Index(fields=['-created_at']),
        ]
        # Empêcher les notations en double pour une même mission
        unique_together = [['notateur', 'mission']]
    
    def __str__(self):
        return f"Notation {self.note_valeur}★ de {self.notateur.get_full_name()} pour {self.note.get_full_name()}"
    
    def clean(self):
        """Validation du modèle"""
        super().clean()
        
        # Vérifier qu'au moins une référence (mission ou contrat) est fournie
        if not self.mission:  # and not self.contrat_saisonnier:
            raise ValidationError("Une notation doit être liée à une mission ou un contrat complété")
        
        # Vérifier que la mission est terminée
        if self.mission and self.mission.statut != 'TERMINEE':
            raise ValidationError("La notation n'est autorisée qu'après la fin de la mission")
        
        # Vérifier que le notateur était bien partie prenante de la mission
        if self.mission:
            if self.notateur not in [self.mission.exploitant, self.mission.agronome]:
                raise ValidationError("Seuls les participants à la mission peuvent la noter")
            
            # Vérifier que l'utilisateur noté est l'autre partie
            if self.notateur == self.mission.exploitant:
                if self.note != self.mission.agronome:
                    raise ValidationError("L'exploitant doit noter l'agronome de la mission")
            else:
                if self.note != self.mission.exploitant:
                    raise ValidationError("L'agronome doit noter l'exploitant de la mission")
        
        # Vérifier qu'on ne se note pas soi-même
        if self.notateur == self.note:
            raise ValidationError("Vous ne pouvez pas vous noter vous-même")


class SignalementNotation(TimeStampedModel):
    """
    Modèle pour les signalements de notations inappropriées
    Exigence: 27.5
    """
    MOTIF_CHOICES = [
        ('INAPPROPRIE', 'Contenu inapproprié'),
        ('FAUX', 'Information fausse'),
        ('SPAM', 'Spam'),
        ('HARCÈLEMENT', 'Harcèlement'),
        ('AUTRE', 'Autre'),
    ]
    
    notation = models.ForeignKey(
        Notation,
        on_delete=models.CASCADE,
        related_name='signalements',
        verbose_name="Notation"
    )
    
    signaleur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='signalements_effectues',
        verbose_name="Signaleur"
    )
    
    motif = models.CharField(
        max_length=20,
        choices=MOTIF_CHOICES,
        verbose_name="Motif"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    
    traite = models.BooleanField(
        default=False,
        verbose_name="Traité"
    )
    
    class Meta:
        verbose_name = "Signalement de notation"
        verbose_name_plural = "Signalements de notations"
        ordering = ['-created_at']
        # Empêcher les signalements en double
        unique_together = [['notation', 'signaleur']]
    
    def __str__(self):
        return f"Signalement de {self.signaleur.get_full_name()} sur notation #{self.notation.id}"
