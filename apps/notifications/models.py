from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel

class Notification(TimeStampedModel):
    TYPES = [
        ('NOUVEAU_MESSAGE', 'Nouveau message'),
        ('MISSION_ACCEPTEE', 'Mission acceptée'),
        ('MISSION_REFUSEE', 'Mission refusée'),
        ('PAIEMENT_RECU', 'Paiement reçu'),
        ('AVIS_RECU', 'Avis reçu'),
        ('CONTRAT_SIGNE', 'Contrat signé'),
        ('PREVENTE_ENGAGEE', 'Prévente engagée'),
        ('ALERTE_SYSTEME', 'Alerte système'),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type_notification = models.CharField(max_length=30, choices=TYPES)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lien = models.CharField(max_length=500, null=True, blank=True)
    lue = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titre} - {self.utilisateur.username}"

class PreferenceNotification(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferences_notification'
    )
    nouveau_message_email = models.BooleanField(default=True)
    mission_acceptee_email = models.BooleanField(default=True)
    paiement_recu_email = models.BooleanField(default=True)

    def __str__(self):
        return f"Préférences de {self.user.username}"
