"""
Tâches Celery pour les paiements
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name='payments.auto_release_escrow')
def auto_release_escrow():
    """
    Libérer automatiquement les fonds escrow dont la date de libération est passée.
    """
    from .models import EscrowAccount

    now = timezone.now()
    escrows = EscrowAccount.objects.filter(
        statut='BLOQUE',
        date_liberation_prevue__lte=now,
    )
    count = 0
    for escrow in escrows:
        try:
            escrow.statut = 'LIBERE'
            escrow.date_liberation_effective = now
            escrow.save(update_fields=['statut', 'date_liberation_effective'])
            count += 1
            logger.info("Escrow #%s libéré automatiquement (%s FCFA)", escrow.id, escrow.montant_bloque)
        except Exception as e:
            logger.error("Erreur libération escrow #%s: %s", escrow.id, e)

    logger.info("Auto-release escrow terminé: %d comptes libérés", count)
    return count


@shared_task(name='payments.reconcile_pending_transactions')
def reconcile_pending_transactions():
    """
    Vérifier les transactions PENDING de plus de 30 minutes auprès de FedaPay
    et mettre à jour leur statut.
    """
    from .models import Transaction
    from .services import FedapayService

    threshold = timezone.now() - timezone.timedelta(minutes=30)
    pending = Transaction.objects.filter(
        statut='PENDING',
        created_at__lte=threshold,
        fedapay_transaction_id__isnull=False,
    )

    service = FedapayService()
    updated = 0
    for tx in pending:
        try:
            result = service._get(f"/transactions/{tx.fedapay_transaction_id}")
            remote_status = result.get('transaction', {}).get('status', '')

            if remote_status == 'approved':
                tx.statut = 'SUCCESS'
                tx.save(update_fields=['statut'])
                updated += 1
            elif remote_status in ('declined', 'canceled', 'refunded'):
                tx.statut = 'FAILED'
                tx.save(update_fields=['statut'])
                updated += 1
        except Exception as e:
            logger.error("Erreur réconciliation transaction %s: %s", tx.id, e)

    logger.info("Réconciliation terminée: %d transactions mises à jour", updated)
    return updated
