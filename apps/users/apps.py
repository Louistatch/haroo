from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Utilisateurs'
    
    def ready(self):
        """
        Importer les signaux lors du démarrage de l'application
        
        Les signaux gèrent l'invalidation automatique du cache Redis
        lorsque les modèles User, AgronomeProfile, etc. sont modifiés.
        """
        import apps.users.signals  # noqa
