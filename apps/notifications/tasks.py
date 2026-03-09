"""
Tâches Celery pour les notifications
"""
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(name='notifications.send_pending_notifications')
def send_pending_notifications():
    """
    Envoyer par email les notifications non lues qui ont des préférences email activées.
    """
    from .models import Notification, PreferenceNotification

    # Notifications non lues des 5 dernières minutes (éviter les doublons)
    from django.utils import timezone
    since = timezone.now() - timezone.timedelta(minutes=5)

    notifications = Notification.objects.filter(
        lue=False,
        created_at__gte=since,
    ).select_related('utilisateur')

    sent = 0
    for notif in notifications:
        user = notif.utilisateur
        if not user.email:
            continue

        # Vérifier les préférences
        try:
            prefs = PreferenceNotification.objects.get(user=user)
            type_key = f"{notif.type_notification.lower()}_email"
            if hasattr(prefs, type_key) and not getattr(prefs, type_key):
                continue
        except PreferenceNotification.DoesNotExist:
            pass  # Pas de préférences = envoyer par défaut

        try:
            send_mail(
                subject=notif.titre,
                message=notif.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            sent += 1
        except Exception as e:
            logger.error("Erreur envoi email notification #%s: %s", notif.id, e)

    logger.info("Notifications email envoyées: %d", sent)
    return sent
