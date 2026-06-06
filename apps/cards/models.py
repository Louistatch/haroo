from django.db import models
from apps.core.models import TimeStampedModel

CARD_TYPE_CHOICES = [
    ('OUVRIER', 'Ouvrier Agricole'),
    ('ACHETEUR', 'Acheteur / Commerce'),
    ('AGRONOME', 'Ingénieur Agronome'),
]


class Card(TimeStampedModel):
    card_number = models.CharField(max_length=20, unique=True, verbose_name="Numéro de carte")
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES)
    statut = models.CharField(
        max_length=20,
        default='active',
        choices=[('active', 'Active'), ('expired', 'Expirée'), ('revoked', 'Révoquée')]
    )
    expiry_date = models.DateField(null=True, blank=True)

    # One of these will be set depending on card_type
    ouvrier = models.OneToOneField(
        'users.OuvrierProfile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='card'
    )
    acheteur = models.OneToOneField(
        'users.AcheteurProfile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='card'
    )
    agronome = models.OneToOneField(
        'users.AgronomeProfile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='card'
    )

    class Meta:
        verbose_name = "Carte Professionnelle"
        verbose_name_plural = "Cartes Professionnelles"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.card_number} ({self.get_card_type_display()})"

    @property
    def is_active(self):
        from datetime import date
        if self.statut != 'active':
            return False
        if self.expiry_date and self.expiry_date < date.today():
            return False
        return True

    def get_holder_name(self):
        if self.card_type == 'OUVRIER' and self.ouvrier:
            return self.ouvrier.user.get_full_name()
        elif self.card_type == 'ACHETEUR' and self.acheteur:
            return self.acheteur.user.get_full_name()
        elif self.card_type == 'AGRONOME' and self.agronome:
            return self.agronome.user.get_full_name()
        return ''

    def get_holder_photo(self):
        user = None
        if self.card_type == 'OUVRIER' and self.ouvrier:
            user = self.ouvrier.user
        elif self.card_type == 'ACHETEUR' and self.acheteur:
            user = self.acheteur.user
        elif self.card_type == 'AGRONOME' and self.agronome:
            user = self.agronome.user
        if user and user.photo_profil:
            return user.photo_profil.url
        return None
