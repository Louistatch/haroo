"""
Signaux pour la conformité réglementaire
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.payments.models import Transaction
from .services import ReceiptService


@receiver(post_save, sender=Transaction)
def create_receipt_on_success(sender, instance, created, **kwargs):
    """
    Crée automatiquement un reçu électronique quand une transaction réussit
    Exigence: 45.5
    """
    # Créer un reçu uniquement pour les transactions réussies
    if instance.statut == 'SUCCESS' and not hasattr(instance, 'receipt'):
        try:
            ReceiptService.create_receipt(instance)
        except Exception as e:
            # Logger l'erreur mais ne pas bloquer la transaction
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de la création du reçu pour la transaction {instance.id}: {e}")
