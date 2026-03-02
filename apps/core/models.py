"""
Modèles de base pour l'application Core
"""
from django.db import models


class TimeStampedModel(models.Model):
    """
    Modèle abstrait avec timestamps automatiques
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    class Meta:
        abstract = True
