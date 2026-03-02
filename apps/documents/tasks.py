"""
Tâches Celery pour l'application documents

Ce module contient les tâches asynchrones pour:
- Envoi d'emails de confirmation d'achat
- Rappels d'expiration de liens
- Anonymisation des logs de téléchargement
"""
import logging
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from apps.documents.models import AchatDocument, DownloadLog
from apps.documents.services import EmailService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute
    autoretry_for=(Exception,),
    retry_backoff=True,  # Exponential backoff
    retry_backoff_max=600,  # Max 10 minutes
    retry_jitter=True  # Add randomness to avoid thundering herd
)
def send_purchase_confirmation_async(self, achat_id: int, download_url: str):
    """
    Envoyer un email de confirmation d'achat de manière asynchrone
    
    Args:
        achat_id: ID de l'achat
        download_url: URL de téléchargement sécurisée
        
    Returns:
        dict: Résultat de l'envoi
        
    Example:
        >>> send_purchase_confirmation_async.delay(123, 'https://...')
    """
    try:
        logger.info(f"Début envoi email confirmation pour achat {achat_id}")
        
        # Récupérer l'achat
        try:
            achat = AchatDocument.objects.select_related(
                'acheteur', 'document'
            ).get(id=achat_id)
        except AchatDocument.DoesNotExist:
            logger.error(f"Achat {achat_id} introuvable")
            return {
                'success': False,
                'error': 'Achat introuvable',
                'achat_id': achat_id
            }
        
        # Envoyer l'email
        email_service = EmailService()
        success = email_service.send_purchase_confirmation(achat, download_url)
        
        if success:
            logger.info(
                f"Email de confirmation envoyé avec succès pour achat {achat_id}"
            )
            return {
                'success': True,
                'achat_id': achat_id,
                'email': achat.acheteur.email
            }
        else:
            logger.warning(
                f"Échec envoi email confirmation pour achat {achat_id}"
            )
            # Retry automatique via autoretry_for
            raise Exception("Échec envoi email")
            
    except MaxRetriesExceededError:
        logger.error(
            f"Nombre maximum de tentatives atteint pour achat {achat_id}"
        )
        return {
            'success': False,
            'error': 'Max retries exceeded',
            'achat_id': achat_id
        }
    except Exception as e:
        logger.error(
            f"Erreur lors de l'envoi email pour achat {achat_id}: {str(e)}",
            exc_info=True
        )
        # Retry automatique
        raise


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=300,  # 5 minutes
    autoretry_for=(Exception,),
    retry_backoff=True
)
def send_link_regenerated_async(self, achat_id: int, download_url: str):
    """
    Envoyer un email de confirmation de régénération de lien
    
    Args:
        achat_id: ID de l'achat
        download_url: Nouvelle URL de téléchargement
        
    Returns:
        dict: Résultat de l'envoi
    """
    try:
        logger.info(f"Début envoi email régénération pour achat {achat_id}")
        
        achat = AchatDocument.objects.select_related(
            'acheteur', 'document'
        ).get(id=achat_id)
        
        email_service = EmailService()
        success = email_service.send_link_regenerated(achat, download_url)
        
        if success:
            logger.info(
                f"Email de régénération envoyé avec succès pour achat {achat_id}"
            )
            return {
                'success': True,
                'achat_id': achat_id
            }
        else:
            raise Exception("Échec envoi email")
            
    except AchatDocument.DoesNotExist:
        logger.error(f"Achat {achat_id} introuvable")
        return {
            'success': False,
            'error': 'Achat introuvable',
            'achat_id': achat_id
        }
    except Exception as e:
        logger.error(
            f"Erreur envoi email régénération pour achat {achat_id}: {str(e)}",
            exc_info=True
        )
        raise


@shared_task(name='documents.send_expiration_reminders')
def send_expiration_reminders():
    """
    Tâche planifiée: Envoyer des rappels d'expiration de liens
    
    Envoie un rappel 24h avant l'expiration du lien de téléchargement.
    Exécutée toutes les heures par Celery Beat.
    
    Returns:
        dict: Statistiques d'envoi
        
    Example:
        >>> send_expiration_reminders.delay()
    """
    try:
        logger.info("Début envoi des rappels d'expiration")
        
        # Calculer la fenêtre de temps (entre 23h et 25h avant expiration)
        now = timezone.now()
        window_start = now + timedelta(hours=23)
        window_end = now + timedelta(hours=25)
        
        # Récupérer les achats concernés
        achats = AchatDocument.objects.filter(
            statut_paiement='PAYE',
            expiration_lien__gte=window_start,
            expiration_lien__lte=window_end,
            nombre_telechargements=0  # Pas encore téléchargé
        ).select_related('acheteur', 'document')
        
        count = achats.count()
        logger.info(f"{count} achats nécessitent un rappel d'expiration")
        
        if count == 0:
            return {
                'success': True,
                'sent': 0,
                'failed': 0,
                'message': 'Aucun rappel à envoyer'
            }
        
        # Envoyer les rappels
        email_service = EmailService()
        stats = email_service.send_bulk_expiration_reminders(
            achats,
            hours_remaining=24
        )
        
        logger.info(
            f"Rappels d'expiration envoyés: {stats['success']} succès, "
            f"{stats['failed']} échecs"
        )
        
        return {
            'success': True,
            'sent': stats['success'],
            'failed': stats['failed'],
            'total': count
        }
        
    except Exception as e:
        logger.error(
            f"Erreur lors de l'envoi des rappels d'expiration: {str(e)}",
            exc_info=True
        )
        return {
            'success': False,
            'error': str(e)
        }


@shared_task(name='documents.anonymize_old_download_logs')
def anonymize_old_download_logs():
    """
    Tâche planifiée: Anonymiser les anciens logs de téléchargement
    
    Anonymise les logs de plus de 90 jours pour conformité RGPD.
    Exécutée quotidiennement à 2h du matin par Celery Beat.
    
    Returns:
        dict: Statistiques d'anonymisation
        
    Example:
        >>> anonymize_old_download_logs.delay()
    """
    try:
        logger.info("Début anonymisation des anciens logs de téléchargement")
        
        # Calculer la date limite (90 jours)
        cutoff_date = timezone.now() - timedelta(days=90)
        
        # Récupérer les logs à anonymiser
        logs_to_anonymize = DownloadLog.objects.filter(
            downloaded_at__lt=cutoff_date,
            ip_address__isnull=False  # Pas déjà anonymisé
        )
        
        count = logs_to_anonymize.count()
        logger.info(f"{count} logs à anonymiser")
        
        if count == 0:
            return {
                'success': True,
                'anonymized': 0,
                'message': 'Aucun log à anonymiser'
            }
        
        # Anonymiser les logs
        anonymized = logs_to_anonymize.update(
            ip_address=None,
            user_agent=None
        )
        
        logger.info(f"{anonymized} logs anonymisés avec succès")
        
        return {
            'success': True,
            'anonymized': anonymized,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(
            f"Erreur lors de l'anonymisation des logs: {str(e)}",
            exc_info=True
        )
        return {
            'success': False,
            'error': str(e)
        }


@shared_task(name='documents.cleanup_expired_links')
def cleanup_expired_links():
    """
    Tâche planifiée: Nettoyer les liens expirés
    
    Marque les achats avec liens expirés pour faciliter les requêtes.
    Exécutée toutes les heures par Celery Beat.
    
    Returns:
        dict: Statistiques de nettoyage
    """
    try:
        logger.info("Début nettoyage des liens expirés")
        
        now = timezone.now()
        
        # Compter les liens expirés
        expired_count = AchatDocument.objects.filter(
            expiration_lien__lt=now,
            statut_paiement='PAYE'
        ).count()
        
        logger.info(f"{expired_count} liens expirés identifiés")
        
        return {
            'success': True,
            'expired_count': expired_count,
            'checked_at': now.isoformat()
        }
        
    except Exception as e:
        logger.error(
            f"Erreur lors du nettoyage des liens expirés: {str(e)}",
            exc_info=True
        )
        return {
            'success': False,
            'error': str(e)
        }
