"""
Package principal Haroo
"""
# Charger Celery au démarrage de Django (skip si non installé, ex: deploy léger)
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    celery_app = None
    __all__ = ()
