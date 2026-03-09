from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from apps.core.models import TimeStampedModel

SEUIL_HECTARES = 10  # Superficie minimum pour publier directement


class AnnonceCollective(TimeStampedModel):
    """
    Annonce collective pour les exploitants avec < 10 ha.
    Les exploitants de la même zone peuvent rejoindre pour atteindre le seuil.
    Durée de vie : 2 jours. Si le seuil n'est pas atteint, l'annonce expire.
    """
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente de participants'),
        ('VALIDEE', 'Quota atteint — publiée'),
        ('EXPIREE', 'Expirée — quota non atteint'),
        ('ANNULEE', 'Annulée'),
    ]

    createur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='annonces_creees',
        verbose_name="Créateur"
    )
    type_travail = models.CharField(max_length=100, verbose_name="Type de travail")
    description = models.TextField(verbose_name="Description")
    canton = models.ForeignKey(
        'locations.Canton',
        on_delete=models.PROTECT,
        verbose_name="Canton"
    )
    date_debut = models.DateField(verbose_name="Date de début des travaux")
    date_fin = models.DateField(verbose_name="Date de fin des travaux")
    salaire_horaire = models.DecimalField(
        max_digits=8, decimal_places=2,
        verbose_name="Salaire horaire proposé (FCFA)"
    )
    nombre_postes = models.IntegerField(verbose_name="Nombre de postes souhaités")
    superficie_cumulee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="Superficie cumulée (ha)"
    )
    seuil_hectares = models.DecimalField(
        max_digits=10, decimal_places=2, default=SEUIL_HECTARES,
        verbose_name="Seuil requis (ha)"
    )
    date_expiration = models.DateTimeField(verbose_name="Date d'expiration")
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES,
        default='EN_ATTENTE', verbose_name="Statut"
    )
    offre_generee = models.OneToOneField(
        'OffreEmploiSaisonnier', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='annonce_source',
        verbose_name="Offre générée"
    )

    class Meta:
        verbose_name = "Annonce collective"
        verbose_name_plural = "Annonces collectives"
        ordering = ['-created_at']

    def __str__(self):
        return f"Annonce #{self.id} — {self.type_travail} à {self.canton} ({self.superficie_cumulee}/{self.seuil_hectares} ha)"

    def save(self, *args, **kwargs):
        if not self.date_expiration:
            self.date_expiration = timezone.now() + timedelta(days=2)
        super().save(*args, **kwargs)

    @property
    def est_expiree(self):
        return timezone.now() > self.date_expiration and self.statut == 'EN_ATTENTE'

    @property
    def quota_atteint(self):
        return self.superficie_cumulee >= self.seuil_hectares


class ParticipationAnnonce(TimeStampedModel):
    """
    Participation d'un exploitant à une annonce collective.
    """
    annonce = models.ForeignKey(
        AnnonceCollective, on_delete=models.CASCADE,
        related_name='participations', verbose_name="Annonce"
    )
    exploitant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='participations_annonces', verbose_name="Exploitant"
    )
    superficie_apportee = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Superficie apportée (ha)"
    )

    class Meta:
        verbose_name = "Participation à annonce"
        verbose_name_plural = "Participations aux annonces"
        unique_together = [['annonce', 'exploitant']]

    def __str__(self):
        return f"{self.exploitant.get_full_name()} — {self.superficie_apportee} ha"


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
        max_digits=8, decimal_places=2,
        verbose_name="Salaire horaire (FCFA)"
    )
    nombre_postes = models.IntegerField(verbose_name="Nombre de postes")
    postes_pourvus = models.IntegerField(default=0, verbose_name="Postes pourvus")
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES,
        default='OUVERTE', verbose_name="Statut"
    )
    est_collective = models.BooleanField(
        default=False,
        verbose_name="Issue d'une annonce collective"
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
        OffreEmploiSaisonnier, on_delete=models.PROTECT, verbose_name="Offre"
    )
    ouvrier = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='contrats_ouvrier', verbose_name="Ouvrier"
    )
    exploitant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='contrats_exploitant', verbose_name="Exploitant"
    )
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    salaire_horaire = models.DecimalField(
        max_digits=8, decimal_places=2,
        verbose_name="Salaire horaire (FCFA)"
    )
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES,
        default='SIGNE', verbose_name="Statut"
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
        ContratSaisonnier, on_delete=models.CASCADE,
        related_name='heures', verbose_name="Contrat"
    )
    date = models.DateField(verbose_name="Date")
    heures = models.DecimalField(
        max_digits=4, decimal_places=2, verbose_name="Heures"
    )
    statut_validation = models.CharField(
        max_length=20, choices=STATUT_CHOICES,
        default='EN_ATTENTE', verbose_name="Statut de validation"
    )
    montant_calcule = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Montant calculé"
    )

    class Meta:
        verbose_name = "Heures travaillées"
        verbose_name_plural = "Heures travaillées"
        unique_together = [['contrat', 'date']]
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.heures}h - {self.contrat.ouvrier.get_full_name()}"



class AnnonceOuvrier(TimeStampedModel):
    """
    Annonce de disponibilité créée par un ouvrier.
    L'ouvrier propose ses services aux exploitants de sa zone.
    Peut être une annonce individuelle (avec équipe complète) ou collective (recrutement d'équipe).
    """
    STATUT_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('EXPIREE', 'Expirée'),
        ('EN_ATTENTE', 'En attente d\'équipe'),
        ('VALIDEE', 'Équipe complète'),
    ]
    
    TYPE_CHOICES = [
        ('INDIVIDUELLE', 'Individuelle - Équipe complète'),
        ('COLLECTIVE', 'Collective - Recrutement d\'équipe'),
    ]

    ouvrier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='annonces_ouvrier',
        verbose_name="Ouvrier"
    )
    type_annonce = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='INDIVIDUELLE',
        verbose_name="Type d'annonce"
    )
    titre = models.CharField(
        max_length=200,
        verbose_name="Titre de l'annonce"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Décrivez vos compétences et votre expérience"
    )
    competences = models.JSONField(
        default=list,
        verbose_name="Compétences",
        help_text="Liste des types de travaux maîtrisés"
    )
    cantons_disponibles = models.ManyToManyField(
        'locations.Canton',
        related_name='annonces_ouvriers',
        verbose_name="Cantons où vous êtes disponible"
    )
    tarif_horaire_min = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Tarif horaire minimum souhaité (FCFA)"
    )
    date_disponibilite_debut = models.DateField(
        verbose_name="Disponible à partir du"
    )
    date_disponibilite_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name="Disponible jusqu'au (optionnel)"
    )
    
    # Informations de l'équipe (pour annonce individuelle)
    equipe_complete = models.BooleanField(
        default=False,
        verbose_name="Équipe de 8 personnes complète"
    )
    membres_equipe = models.JSONField(
        default=list,
        verbose_name="Membres de l'équipe",
        help_text="Liste des 7 autres membres (nom, prénom, téléphone)"
    )
    
    # Pour annonce collective
    nb_membres_actuels = models.IntegerField(
        default=1,
        verbose_name="Nombre de membres actuels"
    )
    membres_rejoints = models.JSONField(
        default=list,
        verbose_name="Membres ayant rejoint",
        help_text="Liste des ouvriers ayant rejoint l'annonce collective"
    )
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='ACTIVE',
        verbose_name="Statut"
    )
    date_expiration = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'expiration"
    )

    class Meta:
        verbose_name = "Annonce d'ouvrier"
        verbose_name_plural = "Annonces d'ouvriers"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titre} - {self.ouvrier.get_full_name()}"

    def save(self, *args, **kwargs):
        # Pour annonce collective, expiration après 2 jours
        if self.type_annonce == 'COLLECTIVE' and not self.date_expiration:
            self.date_expiration = timezone.now() + timedelta(days=2)
        # Pour annonce individuelle, expiration après 30 jours
        elif self.type_annonce == 'INDIVIDUELLE' and not self.date_expiration:
            self.date_expiration = timezone.now() + timedelta(days=30)
        
        # Vérifier si l'équipe est complète pour annonce collective
        if self.type_annonce == 'COLLECTIVE' and self.nb_membres_actuels >= 8:
            self.statut = 'VALIDEE'
            self.equipe_complete = True
        
        super().save(*args, **kwargs)

    @property
    def est_expiree(self):
        return (
            self.date_expiration and timezone.now() > self.date_expiration
        ) or (
            self.date_disponibilite_fin and timezone.now().date() > self.date_disponibilite_fin
        )
    
    @property
    def progression(self):
        """Pourcentage de progression pour annonce collective"""
        if self.type_annonce == 'COLLECTIVE':
            return (self.nb_membres_actuels / 8) * 100
        return 100 if self.equipe_complete else 0
