"""
Modèles pour le découpage administratif du Togo
"""
from django.db import models
from apps.core.models import TimeStampedModel

# Essayer d'importer PostGIS, sinon utiliser des champs standards
try:
    from django.contrib.gis.db import models as gis_models
    HAS_GIS = True
except (ImportError, Exception):
    HAS_GIS = False


class Region(TimeStampedModel):
    """
    Modèle pour les régions du Togo (5 régions)
    """
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")

    class Meta:
        verbose_name = "Région"
        verbose_name_plural = "Régions"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Prefecture(TimeStampedModel):
    """
    Modèle pour les préfectures du Togo (39 préfectures)
    """
    nom = models.CharField(max_length=100, verbose_name="Nom")
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name='prefectures',
        verbose_name="Région"
    )

    class Meta:
        verbose_name = "Préfecture"
        verbose_name_plural = "Préfectures"
        ordering = ['nom']
        unique_together = [['nom', 'region']]

    def __str__(self):
        return f"{self.nom} ({self.region.nom})"


class Canton(TimeStampedModel):
    """
    Modèle pour les cantons du Togo (300+ cantons)
    """
    nom = models.CharField(max_length=100, verbose_name="Nom")
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    prefecture = models.ForeignKey(
        Prefecture,
        on_delete=models.PROTECT,
        related_name='cantons',
        verbose_name="Préfecture"
    )
    
    # Utiliser PointField si PostGIS est disponible, sinon JSONField
    if HAS_GIS:
        coordonnees_centre = gis_models.PointField(
            geography=True,
            null=True,
            blank=True,
            verbose_name="Coordonnées du centre"
        )
    else:
        # Stocker les coordonnées en JSON: {"lat": float, "lon": float}
        coordonnees_centre = models.JSONField(
            null=True,
            blank=True,
            verbose_name="Coordonnées du centre",
            help_text='Format: {"lat": latitude, "lon": longitude}'
        )

    class Meta:
        verbose_name = "Canton"
        verbose_name_plural = "Cantons"
        ordering = ['nom']
        unique_together = [['nom', 'prefecture']]
        indexes = [
            models.Index(fields=['nom']),
        ]

    def __str__(self):
        return f"{self.nom} ({self.prefecture.nom})"
