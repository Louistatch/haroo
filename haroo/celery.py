"""
Configuration Celery pour Haroo
"""
import os
from celery import Celery

# Définir le module de settings Django par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haroo.settings.dev')

app = Celery('haroo')

# Charger la configuration depuis les settings Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tâches dans les apps Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Tâche de debug"""
    print(f'Request: {self.request!r}')
