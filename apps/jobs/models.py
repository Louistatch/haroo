from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel


class OffreEmploiSaisonnier(TimeStampedModel):
    STATUT_CHOICES = [
        ('OUVERTE', 'Ouverte'),
        ('POURVUE', 'Pourvue'),
        ('EXPIREE', 'Expirée'),
    ]

    exploitant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='offres_emploi',
        verbose_name="Exploitant"
    )
    type_travail = models.CharField(max_length=100, verbose_name="Type de travail")
    description = models.TextField(verbose_name="Description")
    canton = models.ForeignKey(
        'locations.Canton',
        on_delete=models.PROTECT,
        verbose_name="Canton"
    )
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    salaire_horaire = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Salaire horaire (FCFA)"
    )
    nombre_postes = models.IntegerField(verbose_name="Nombre de postes")
    postes_pourvus = models.IntegerField(default=0, verbose_name="Postes pourvus")
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='OUVERTE',
        verbose_name="Statut"
    )

    class Meta:
        verbose_name = "Offre d'emploi saisonnier"
        verbose_name_plural = "Offres d'emploi saisonnier"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.type_travail} - {self.exploitant.get_full_name()}"


class ContratSaisonnier(TimeStampedModel):
    STATUT_CHOICES = [
        ('SIGNE', 'Signé'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    ]

    offre = models.ForeignKey(
        OffreEmploiSaisonnier,
        on_delete=models.PROTECT,
        verbose_name="Offre"
    )
    ouvrier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='contrats_ouvrier',
        verbose_name="Ouvrier"
    )
    exploitant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='contrats_exploitant',
        verbose_name="Exploitant"
    )
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    salaire_horaire = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Salaire horaire (FCFA)"
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='SIGNE',
        verbose_name="Statut"
    )

    class Meta:
        verbose_name = "Contrat saisonnier"
        verbose_name_plural = "Contrats saisonniers"
        ordering = ['-created_at']

    def __str__(self):
        return f"Contrat #{self.id} - {self.ouvrier.get_full_name()}"


class HeuresTravaillees(TimeStampedModel):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('VALIDEE', 'Validée'),
        ('CONTESTEE', 'Contestée'),
    ]

    contrat = models.ForeignKey(
        ContratSaisonnier,
        on_delete=models.CASCADE,
        related_name='heures',
        verbose_name="Contrat"
    )
    date = models.DateField(verbose_name="Date")
    heures = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Heures"
    )
    statut_validation = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE',
        verbose_name="Statut de validation"
    )
    montant_calcule = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Montant calculé"
    )

    class Meta:
        verbose_name = "Heures travaillées"
        verbose_name_plural = "Heures travaillées"
        unique_together = [['contrat', 'date']]
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.heures}h - {self.contrat.ouvrier.get_full_name()}"
