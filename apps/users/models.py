"""
Modèles pour la gestion des utilisateurs
"""
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

# Essayer d'importer PostGIS, sinon utiliser des champs standards
try:
    from django.contrib.gis.db import models as gis_models
    HAS_GIS = True
except (ImportError, Exception):
    HAS_GIS = False


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé pour Haroo
    """
    USER_TYPE_CHOICES = [
        ('EXPLOITANT', 'Exploitant'),
        ('AGRONOME', 'Agronome'),
        ('OUVRIER', 'Ouvrier Agricole'),
        ('ACHETEUR', 'Acheteur'),
        ('INSTITUTION', 'Institution'),
        ('ADMIN', 'Administrateur'),
    ]
    
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="Numéro de téléphone"
    )
    phone_verified = models.BooleanField(
        default=False,
        verbose_name="Téléphone vérifié"
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        verbose_name="Type d'utilisateur"
    )
    two_factor_enabled = models.BooleanField(
        default=False,
        verbose_name="2FA activé"
    )
    two_factor_secret = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name="Secret 2FA"
    )
    photo_profil = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
        verbose_name="Photo de profil"
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
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class ExploitantProfile(models.Model):
    """
    Profil pour les exploitants agricoles
    Exigences: 2.1, 2.5, 10.1
    """
    STATUT_VERIFICATION_CHOICES = [
        ('NON_VERIFIE', 'Non Vérifié'),
        ('EN_ATTENTE', 'En Attente de Vérification'),
        ('VERIFIE', 'Vérifié'),
        ('REJETE', 'Rejeté'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='exploitant_profile',
        verbose_name="Utilisateur"
    )
    superficie_totale = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Superficie totale (hectares)",
        help_text="Superficie totale de l'exploitation en hectares"
    )
    canton_principal = models.ForeignKey(
        'locations.Canton',
        on_delete=models.PROTECT,
        verbose_name="Canton principal"
    )
    
    # Utiliser PointField si PostGIS est disponible, sinon JSONField
    if HAS_GIS:
        coordonnees_gps = gis_models.PointField(
            geography=True,
            verbose_name="Coordonnées GPS"
        )
    else:
        coordonnees_gps = models.JSONField(
            verbose_name="Coordonnées GPS",
            help_text='Format: {"lat": latitude, "lon": longitude}'
        )
    
    statut_verification = models.CharField(
        max_length=20,
        choices=STATUT_VERIFICATION_CHOICES,
        default='NON_VERIFIE',
        verbose_name="Statut de vérification"
    )
    date_verification = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de vérification"
    )
    motif_rejet = models.TextField(
        null=True,
        blank=True,
        verbose_name="Motif de rejet",
        help_text="Raison du rejet de la demande de vérification"
    )
    cultures_actuelles = models.JSONField(
        default=list,
        verbose_name="Cultures actuelles",
        help_text="Liste des cultures actuellement cultivées"
    )

    class Meta:
        verbose_name = "Profil Exploitant"
        verbose_name_plural = "Profils Exploitants"
        indexes = [
            models.Index(fields=['statut_verification']),
        ]

    def __str__(self):
        return f"Exploitant: {self.user.username} - {self.superficie_totale}ha"

    def clean(self):
        """Validation personnalisée pour la superficie"""
        from django.core.exceptions import ValidationError
        if self.superficie_totale and self.superficie_totale < 0:
            raise ValidationError({
                'superficie_totale': 'La superficie ne peut pas être négative.'
            })


class AgronomeProfile(models.Model):
    """
    Profil pour les agronomes
    Exigences: 2.1, 2.5, 7.1, 7.3, 7.5
    """
    STATUT_VALIDATION_CHOICES = [
        ('EN_ATTENTE', 'En Attente de Validation'),
        ('VALIDE', 'Validé'),
        ('REJETE', 'Rejeté'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='agronome_profile',
        verbose_name="Utilisateur"
    )
    canton_rattachement = models.ForeignKey(
        'locations.Canton',
        on_delete=models.PROTECT,
        verbose_name="Canton de rattachement"
    )
    specialisations = models.JSONField(
        default=list,
        verbose_name="Spécialisations",
        help_text="Liste des spécialisations agricoles"
    )
    statut_validation = models.CharField(
        max_length=20,
        choices=STATUT_VALIDATION_CHOICES,
        default='EN_ATTENTE',
        verbose_name="Statut de validation"
    )
    badge_valide = models.BooleanField(
        default=False,
        verbose_name="Badge validé"
    )
    date_validation = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de validation"
    )
    motif_rejet = models.TextField(
        null=True,
        blank=True,
        verbose_name="Motif de rejet",
        help_text="Raison du rejet de la demande de validation"
    )
    note_moyenne = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
        verbose_name="Note moyenne"
    )
    nombre_avis = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Nombre d'avis"
    )

    class Meta:
        verbose_name = "Profil Agronome"
        verbose_name_plural = "Profils Agronomes"
        indexes = [
            models.Index(fields=['statut_validation', 'canton_rattachement']),
        ]

    def __str__(self):
        return f"Agronome: {self.user.username} - {self.get_statut_validation_display()}"


class DocumentJustificatif(models.Model):
    """
    Documents justificatifs pour la validation des agronomes
    Exigences: 7.4, 31.1, 31.3
    """
    TYPE_DOCUMENT_CHOICES = [
        ('DIPLOME', 'Diplôme'),
        ('CERTIFICATION', 'Certification'),
        ('PIECE_IDENTITE', 'Pièce d\'identité'),
        ('AUTRE', 'Autre'),
    ]
    
    agronome_profile = models.ForeignKey(
        AgronomeProfile,
        on_delete=models.CASCADE,
        related_name='documents_justificatifs',
        verbose_name="Profil agronome"
    )
    type_document = models.CharField(
        max_length=20,
        choices=TYPE_DOCUMENT_CHOICES,
        verbose_name="Type de document"
    )
    fichier = models.FileField(
        upload_to='agronomists/justificatifs/',
        verbose_name="Fichier"
    )
    nom_fichier = models.CharField(
        max_length=255,
        verbose_name="Nom du fichier"
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'upload"
    )

    class Meta:
        verbose_name = "Document Justificatif"
        verbose_name_plural = "Documents Justificatifs"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.get_type_document_display()} - {self.agronome_profile.user.username}"


class FarmVerificationDocument(models.Model):
    """
    Documents justificatifs pour la vérification des exploitations
    Exigences: 10.3, 31.1, 31.3
    """
    TYPE_DOCUMENT_CHOICES = [
        ('TITRE_FONCIER', 'Titre Foncier'),
        ('CERTIFICAT_EXPLOITATION', 'Certificat d\'Exploitation'),
        ('PHOTO_AERIENNE', 'Photo Aérienne'),
        ('AUTRE', 'Autre'),
    ]
    
    exploitant_profile = models.ForeignKey(
        ExploitantProfile,
        on_delete=models.CASCADE,
        related_name='documents_verification',
        verbose_name="Profil exploitant"
    )
    type_document = models.CharField(
        max_length=30,
        choices=TYPE_DOCUMENT_CHOICES,
        verbose_name="Type de document"
    )
    fichier = models.FileField(
        upload_to='farms/verification/',
        verbose_name="Fichier"
    )
    nom_fichier = models.CharField(
        max_length=255,
        verbose_name="Nom du fichier"
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'upload"
    )

    class Meta:
        verbose_name = "Document de Vérification d'Exploitation"
        verbose_name_plural = "Documents de Vérification d'Exploitations"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.get_type_document_display()} - {self.exploitant_profile.user.username}"





class OuvrierProfile(models.Model):
    """
    Profil pour les ouvriers agricoles
    Exigences: 2.1, 2.5, 12.1
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='ouvrier_profile',
        verbose_name="Utilisateur"
    )
    competences = models.JSONField(
        default=list,
        verbose_name="Compétences",
        help_text="Liste des compétences agricoles"
    )
    cantons_disponibles = models.ManyToManyField(
        'locations.Canton',
        related_name='ouvriers_disponibles',
        verbose_name="Cantons disponibles",
        blank=True
    )
    note_moyenne = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
        verbose_name="Note moyenne"
    )
    nombre_avis = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Nombre d'avis"
    )
    disponible = models.BooleanField(
        default=True,
        verbose_name="Disponible"
    )

    class Meta:
        verbose_name = "Profil Ouvrier"
        verbose_name_plural = "Profils Ouvriers"

    def __str__(self):
        return f"Ouvrier: {self.user.username} - {'Disponible' if self.disponible else 'Non disponible'}"


class AcheteurProfile(models.Model):
    """
    Profil pour les acheteurs
    Exigences: 2.1, 2.5
    """
    TYPE_ACHETEUR_CHOICES = [
        ('PARTICULIER', 'Particulier'),
        ('ENTREPRISE', 'Entreprise'),
        ('COOPERATIVE', 'Coopérative'),
        ('EXPORTATEUR', 'Exportateur'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='acheteur_profile',
        verbose_name="Utilisateur"
    )
    type_acheteur = models.CharField(
        max_length=20,
        choices=TYPE_ACHETEUR_CHOICES,
        default='PARTICULIER',
        verbose_name="Type d'acheteur"
    )
    volume_achats_annuel = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Volume d'achats annuel (tonnes)",
        help_text="Volume d'achats annuel estimé en tonnes"
    )

    class Meta:
        verbose_name = "Profil Acheteur"
        verbose_name_plural = "Profils Acheteurs"

    def __str__(self):
        return f"Acheteur: {self.user.username} - {self.get_type_acheteur_display()}"


class InstitutionProfile(models.Model):
    """
    Profil pour les institutions (ministères, organismes gouvernementaux)
    Exigences: 2.1, 2.5, 25.1, 25.2
    """
    NIVEAU_ACCES_CHOICES = [
        ('NATIONAL', 'National'),
        ('REGIONAL', 'Régional'),
        ('PREFECTORAL', 'Préfectoral'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='institution_profile',
        verbose_name="Utilisateur"
    )
    nom_organisme = models.CharField(
        max_length=200,
        verbose_name="Nom de l'organisme"
    )
    niveau_acces = models.CharField(
        max_length=20,
        choices=NIVEAU_ACCES_CHOICES,
        verbose_name="Niveau d'accès"
    )
    regions_acces = models.ManyToManyField(
        'locations.Region',
        blank=True,
        verbose_name="Régions d'accès",
        help_text="Régions auxquelles l'institution a accès (vide = toutes)"
    )

    class Meta:
        verbose_name = "Profil Institution"
        verbose_name_plural = "Profils Institutions"

    def __str__(self):
        return f"Institution: {self.nom_organisme} - {self.get_niveau_acces_display()}"
