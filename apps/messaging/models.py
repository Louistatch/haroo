from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel

class Conversation(TimeStampedModel):
    MISSION = 'MISSION'
    CONTRAT_SAISONNIER = 'CONTRAT_SAISONNIER'
    GENERAL = 'GENERAL'
    
    TYPE_RELATION_CHOICES = [
        (MISSION, 'Mission'),
        (CONTRAT_SAISONNIER, 'Contrat Saisonnier'),
        (GENERAL, 'Général'),
    ]

    participant_1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='conversations_p1',
        verbose_name="Participant 1"
    )
    participant_2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='conversations_p2',
        verbose_name="Participant 2"
    )
    type_relation = models.CharField(
        max_length=30, 
        choices=TYPE_RELATION_CHOICES,
        default=GENERAL,
        verbose_name="Type de relation"
    )
    reference_id = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="ID de référence"
    )
    derniere_activite = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière activité"
    )

    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        unique_together = [['participant_1', 'participant_2', 'type_relation', 'reference_id']]
        ordering = ['-derniere_activite']

    def __str__(self):
        return f"Conversation {self.id}: {self.participant_1} & {self.participant_2} ({self.type_relation})"

class Message(TimeStampedModel):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Conversation"
    )
    expediteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='messages_envoyes',
        verbose_name="Expéditeur"
    )
    contenu = models.TextField(verbose_name="Contenu", blank=True, default='')
    fichier = models.FileField(
        upload_to='messages/fichiers/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Fichier joint"
    )
    nom_fichier = models.CharField(max_length=255, blank=True, default='', verbose_name="Nom du fichier")
    taille_fichier = models.IntegerField(default=0, verbose_name="Taille du fichier (octets)")
    lu = models.BooleanField(default=False, verbose_name="Lu")
    date_lecture = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de lecture"
    )
    signale = models.BooleanField(default=False, verbose_name="Signalé")
    motif_signalement = models.CharField(max_length=255, blank=True, default='', verbose_name="Motif du signalement")

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 Mo

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['created_at']

    def __str__(self):
        return f"Message {self.id} de {self.expediteur} (Conv {self.conversation_id})"
