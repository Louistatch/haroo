"""
Configuration Celery pour Haroo - Plateforme Agricole Intelligente du Togo

Ce module configure Celery pour les tâches asynchrones:
- Envoi d'emails
- Tâches planifiées (Beat)
- Retry avec exponential backoff
"""
import os
from celery import Celery
from celery.schedules import crontab

# Définir le module de settings Django par défaut
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haroo.settings.dev')

app = Celery('haroo')

# Charger la configuration depuis les settings Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tâches dans les apps Django
app.autodiscover_tasks()

# Configuration Celery Beat - Tâches planifiées
app.conf.beat_schedule = {
    # Envoyer les rappels d'expiration toutes les heures
    'send-expiration-reminders-hourly': {
        'task': 'documents.send_expiration_reminders',
        'schedule': crontab(minute=0),  # Toutes les heures à la minute 0
        'options': {
            'expires': 3600,  # Expire après 1 heure
        }
    },
    
    # Anonymiser les anciens logs quotidiennement à 2h du matin
    'anonymize-old-logs-daily': {
        'task': 'documents.anonymize_old_download_logs',
        'schedule': crontab(hour=2, minute=0),  # Tous les jours à 2h00
        'options': {
            'expires': 86400,  # Expire après 24 heures
        }
    },
    
    # Nettoyer les liens expirés toutes les heures
    'cleanup-expired-links-hourly': {
        'task': 'documents.cleanup_expired_links',
        'schedule': crontab(minute=30),  # Toutes les heures à la minute 30
        'options': {
            'expires': 3600,
        }
    },
}

# Configuration du timezone
app.conf.timezone = 'Africa/Lome'

# Configuration des résultats
app.conf.result_expires = 3600  # Les résultats expirent après 1 heure

# Configuration de la sérialisation
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# Configuration des retry
app.conf.task_acks_late = True  # Acknowledge après exécution
app.conf.task_reject_on_worker_lost = True  # Rejeter si worker crash


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tâche de debug pour tester Celery"""
    print(f'Request: {self.request!r}')
    return 'Debug task executed successfully'
