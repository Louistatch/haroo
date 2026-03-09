"""
Modèles pour la gestion des documents techniques
"""
from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel
from apps.locations.models import Region, Prefecture, Canton


class DocumentTemplate(TimeStampedModel):
    """
    Template de document avec variables dynamiques
    """
    TYPE_CHOICES = [
        ('COMPTE_EXPLOITATION', "Compte d'Exploitation Prévisionnel"),
        ('ITINERAIRE_TECHNIQUE', 'Itinéraire Technique'),
    ]
    
    FORMAT_CHOICES = [
        ('EXCEL', 'Excel'),
        ('WORD', 'Word'),
    ]
    
    titre = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    type_document = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        verbose_name="Type de document"
    )
    format_fichier = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        verbose_name="Format"
    )
    fichier_template = models.FileField(
        upload_to='templates/',
        verbose_name="Fichier template"
    )
    variables_requises = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Variables requises",
        help_text="Liste JSON des variables du template, ex: [\"culture\", \"superficie\"]. Laisser vide si aucune."
    )
    version = models.IntegerField(default=1, verbose_name="Version")

    class Meta:
        verbose_name = "Template de document"
        verbose_name_plural = "Templates de documents"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titre} (v{self.version})"


class DocumentTechnique(TimeStampedModel):
    """
    Document technique généré à partir d'un template
    """
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.PROTECT,
        verbose_name="Template"
    )
    titre = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    prix = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix (FCFA)"
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Région"
    )
    prefecture = models.ForeignKey(
        Prefecture,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Préfecture"
    )
    canton = models.ForeignKey(
        Canton,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Canton"
    )
    culture = models.CharField(max_length=100, verbose_name="Culture")
    fichier_genere = models.FileField(
        upload_to='documents/',
        verbose_name="Fichier généré"
    )
    actif = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Document technique"
        verbose_name_plural = "Documents techniques"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['culture', 'canton']),
            models.Index(fields=['actif']),
        ]

    def __str__(self):
        return self.titre


class AchatDocument(TimeStampedModel):
    """
    Achat d'un document technique par un utilisateur
    """
    acheteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="Acheteur"
    )
    document = models.ForeignKey(
        DocumentTechnique,
        on_delete=models.PROTECT,
        verbose_name="Document"
    )
    transaction = models.OneToOneField(
        'payments.Transaction',
        on_delete=models.PROTECT,
        verbose_name="Transaction"
    )
    lien_telechargement = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Lien de téléchargement"
    )
    expiration_lien = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expiration du lien"
    )
    nombre_telechargements = models.IntegerField(
        default=0,
        verbose_name="Nombre de téléchargements"
    )

    class Meta:
        verbose_name = "Achat de document"
        verbose_name_plural = "Achats de documents"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['acheteur', 'created_at']),
        ]

    def __str__(self):
        return f"{self.acheteur.get_full_name()} - {self.document.titre}"


class DownloadLog(TimeStampedModel):
    """
    Enregistrement des téléchargements avec horodatage et adresse IP
    """
    achat = models.ForeignKey(
        AchatDocument,
        on_delete=models.CASCADE,
        related_name='downloads',
        verbose_name="Achat"
    )
    ip_address = models.GenericIPAddressField(verbose_name="Adresse IP")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Horodatage")

    class Meta:
        verbose_name = "Log de téléchargement"
        verbose_name_plural = "Logs de téléchargement"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['achat', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.achat.document.titre} - {self.ip_address} - {self.timestamp}"
