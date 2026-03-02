"""
Configuration de l'application compliance
"""
from django.apps import AppConfig


class ComplianceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.compliance'
    verbose_name = 'Conformité Réglementaire'
    
    def ready(self):
        """Initialisation de l'application"""
        # Importer les signaux
        import apps.compliance.signals
