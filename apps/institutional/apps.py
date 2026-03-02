"""
Configuration de l'app institutional
"""
from django.apps import AppConfig


class InstitutionalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.institutional'
    verbose_name = 'Dashboard Institutionnel'
