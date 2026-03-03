"""
Services pour la gestion des paiements via Fedapay
"""
import fedapay
from django.conf import settings
from django.urls import reverse
from decimal import Decimal
from typing import Dict, Optional
import logging

from .models import Transaction

logger = logging.getLogger(__name__)


class FedapayService:
    """
    Service d'intégration avec l'API Fedapay pour les paiements mobiles
    """
    
    def __init__(self):
        """Initialiser la configuration Fedapay"""
        fedapay.api_key = settings.FEDAPAY_API_KEY
        fedapay.environment = settings.FEDAPAY_ENVIRONMENT
        
    def initiate_payment(
        self,
        transaction: Transaction,
        callback_url: str,
        description: str = ""
    ) -> Dict[str, any]:
        """
        Initier un paiement via Fedapay
        
        Args:
            transaction: Instance de Transaction Django
            callback_url: URL de retour après paiement
            description: Description du paiement
            
        Returns:
            Dict contenant l'URL de redirection et les détails de la transaction Fedapay
            
        Raises:
            Exception: Si l'initialisation du paiement échoue
        """
        try:
            # Créer la transaction Fedapay
            fedapay_transaction = fedapay.Transaction.create({
                "description": description or f"Paiement {transaction.get_type_transaction_display()}",
                "amount": int(transaction.montant),  # Fedapay attend un entier (montant en centimes)
                "currency": {
                    "iso": "XOF"  # Franc CFA
                },
                "callback_url": callback_url,
                "customer": {
                    "firstname": transaction.utilisateur.first_name or "Client",
                    "lastname": transaction.utilisateur.last_name or "Haroo",
                    "email": transaction.utilisateur.email or f"user{transaction.utilisateur.id}@haroo.tg",
                    "phone_number": {
                        "number": transaction.utilisateur.phone_number,
                        "country": "tg"
                    }
                },
                "custom_metadata": {
                    "transaction_id": str(transaction.id),
                    "user_id": str(transaction.utilisateur.id),
                    "type": transaction.type_transaction
                }
            })
            
            # Mettre à jour la transaction avec l'ID Fedapay
            transaction.fedapay_transaction_id = str(fedapay_transaction.id)
            transaction.save(update_fields=['fedapay_transaction_id', 'updated_at'])
            
            # Générer le token de paiement
            token = fedapay_transaction.generateToken()
            
            logger.info(
                f"Paiement Fedapay initié: transaction_id={transaction.id}, "
                f"fedapay_id={fedapay_transaction.id}"
            )
            
            return {
                "success": True,
                "transaction_id": str(transaction.id),
                "fedapay_transaction_id": str(fedapay_transaction.id),
                "payment_url": token.url,
                "token": token.token
            }
            
        except Exception as e:
            logger.error(
                f"Erreur lors de l'initialisation du paiement Fedapay: {str(e)}, "
                f"transaction_id={transaction.id}"
            )
            # Marquer la transaction comme échouée
            transaction.statut = 'FAILED'
            transaction.save(update_fields=['statut', 'updated_at'])
            
            raise Exception(f"Échec de l'initialisation du paiement: {str(e)}")
    
    def get_transaction_status(self, fedapay_transaction_id: str) -> Dict[str, any]:
        """
        Récupérer le statut d'une transaction Fedapay
        
        Args:
            fedapay_transaction_id: ID de la transaction Fedapay
            
        Returns:
            Dict contenant le statut et les détails de la transaction
        """
        try:
            fedapay_transaction = fedapay.Transaction.retrieve(fedapay_transaction_id)
            
            return {
                "id": str(fedapay_transaction.id),
                "status": fedapay_transaction.status,
                "amount": fedapay_transaction.amount,
                "currency": fedapay_transaction.currency.iso,
                "description": fedapay_transaction.description,
                "created_at": fedapay_transaction.created_at,
                "updated_at": fedapay_transaction.updated_at
            }
            
        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération du statut Fedapay: {str(e)}, "
                f"fedapay_transaction_id={fedapay_transaction_id}"
            )
            raise Exception(f"Impossible de récupérer le statut de la transaction: {str(e)}")
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Vérifier la signature d'un webhook Fedapay
        
        Args:
            payload: Corps de la requête webhook
            signature: Signature fournie dans les headers (hex ou sha256=hex)
            
        Returns:
            True si la signature est valide, False sinon
        """
        try:
            import hmac
            import hashlib

            if not settings.FEDAPAY_WEBHOOK_SECRET:
                logger.warning("FEDAPAY_WEBHOOK_SECRET non configuré — vérification ignorée en dev")
                return True

            expected = hmac.new(
                settings.FEDAPAY_WEBHOOK_SECRET.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            # FedaPay peut envoyer "sha256=<hex>" ou directement "<hex>"
            sig = signature.removeprefix('sha256=')

            return hmac.compare_digest(expected, sig)

        except Exception as e:
            logger.error(f"Erreur vérification signature webhook: {str(e)}")
            return False


class TransactionService:
    """
    Service pour la gestion des transactions
    """
    
    @staticmethod
    def create_transaction(
        utilisateur,
        type_transaction: str,
        montant: Decimal,
        reference_externe: Optional[str] = None
    ) -> Transaction:
        """
        Créer une nouvelle transaction
        
        Args:
            utilisateur: Instance User
            type_transaction: Type de transaction (ACHAT_DOCUMENT, etc.)
            montant: Montant en FCFA
            reference_externe: Référence externe optionnelle (ID document, mission, etc.)
            
        Returns:
            Instance Transaction créée
        """
        # Calculer la commission selon le type
        commission = TransactionService._calculate_commission(type_transaction, montant)
        
        transaction = Transaction.objects.create(
            utilisateur=utilisateur,
            type_transaction=type_transaction,
            montant=montant,
            commission_plateforme=commission,
            reference_externe=reference_externe,
            statut='PENDING'
        )
        
        logger.info(
            f"Transaction créée: id={transaction.id}, type={type_transaction}, "
            f"montant={montant}, commission={commission}"
        )
        
        return transaction
    
    @staticmethod
    def _calculate_commission(type_transaction: str, montant: Decimal) -> Decimal:
        """
        Calculer la commission selon le type de transaction
        
        Args:
            type_transaction: Type de transaction
            montant: Montant de la transaction
            
        Returns:
            Montant de la commission
        """
        commission_rates = {
            'ACHAT_DOCUMENT': 0,  # Pas de commission sur les documents
            'RECRUTEMENT_AGRONOME': settings.COMMISSION_AGRONOME,
            'PREVENTE': settings.COMMISSION_PREVENTE,
            'TRANSPORT': settings.COMMISSION_TRANSPORT,
            'ABONNEMENT': 0  # Pas de commission sur les abonnements
        }
        
        rate = commission_rates.get(type_transaction, 0)
        commission = (montant * Decimal(rate)) / Decimal(100)
        
        return commission.quantize(Decimal('0.01'))  # Arrondir à 2 décimales
    
    @staticmethod
    def update_transaction_status(
        transaction: Transaction,
        new_status: str,
        fedapay_data: Optional[Dict] = None
    ) -> Transaction:
        """
        Mettre à jour le statut d'une transaction
        
        Args:
            transaction: Instance Transaction
            new_status: Nouveau statut
            fedapay_data: Données optionnelles de Fedapay
            
        Returns:
            Transaction mise à jour
        """
        old_status = transaction.statut
        transaction.statut = new_status
        transaction.save(update_fields=['statut', 'updated_at'])
        
        logger.info(
            f"Statut transaction mis à jour: id={transaction.id}, "
            f"{old_status} -> {new_status}"
        )
        
        return transaction


class CommissionCalculator:
    """
    Service pour le calcul des commissions
    """
    
    @staticmethod
    def get_commission_rate(type_transaction: str) -> int:
        """
        Obtenir le taux de commission pour un type de transaction
        
        Args:
            type_transaction: Type de transaction
            
        Returns:
            Taux de commission en pourcentage
        """
        rates = {
            'ACHAT_DOCUMENT': 0,
            'RECRUTEMENT_AGRONOME': settings.COMMISSION_AGRONOME,
            'PREVENTE': settings.COMMISSION_PREVENTE,
            'TRANSPORT': settings.COMMISSION_TRANSPORT,
            'ABONNEMENT': 0
        }
        
        return rates.get(type_transaction, 0)
    
    @staticmethod
    def calculate_net_amount(montant: Decimal, commission: Decimal) -> Decimal:
        """
        Calculer le montant net après commission
        
        Args:
            montant: Montant brut
            commission: Montant de la commission
            
        Returns:
            Montant net
        """
        net = montant - commission
        return net.quantize(Decimal('0.01'))


class EscrowService:
    """
    Service pour la gestion des paiements en escrow (séquestre)
    Retient les paiements jusqu'à confirmation de fin de service
    """
    
    @staticmethod
    def create_escrow(
        transaction,
        beneficiaire,
        montant_bloque: Decimal,
        date_liberation_prevue
    ):
        """
        Créer un compte escrow pour retenir un paiement
        
        Args:
            transaction: Instance Transaction
            beneficiaire: Utilisateur qui recevra le paiement
            montant_bloque: Montant à bloquer en FCFA
            date_liberation_prevue: Date prévue de libération
            
        Returns:
            Instance EscrowAccount créée
        """
        from .models import EscrowAccount
        
        escrow = EscrowAccount.objects.create(
            transaction=transaction,
            montant_bloque=montant_bloque,
            beneficiaire=beneficiaire,
            statut='BLOQUE',
            date_liberation_prevue=date_liberation_prevue
        )
        
        logger.info(
            f"Escrow créé: id={escrow.id}, transaction={transaction.id}, "
            f"beneficiaire={beneficiaire.id}, montant={montant_bloque}"
        )
        
        return escrow
    
    @staticmethod
    def release_escrow(escrow_id: int) -> Dict[str, any]:
        """
        Libérer un paiement en escrow et transférer au bénéficiaire
        Déduit la commission plateforme avant le transfert
        
        Args:
            escrow_id: ID du compte escrow
            
        Returns:
            Dict avec les détails du transfert
            
        Raises:
            ValueError: Si l'escrow n'existe pas ou n'est pas en statut BLOQUE
        """
        from .models import EscrowAccount
        from django.utils import timezone
        
        try:
            escrow = EscrowAccount.objects.select_related(
                'transaction', 'beneficiaire'
            ).get(id=escrow_id)
        except EscrowAccount.DoesNotExist:
            raise ValueError(f"Compte escrow {escrow_id} introuvable")
        
        if escrow.statut != 'BLOQUE':
            raise ValueError(
                f"Le compte escrow {escrow_id} n'est pas en statut BLOQUE "
                f"(statut actuel: {escrow.statut})"
            )
        
        # Calculer le montant net après commission
        commission = escrow.transaction.commission_plateforme
        montant_net = CommissionCalculator.calculate_net_amount(
            escrow.montant_bloque,
            commission
        )
        
        # Mettre à jour le statut de l'escrow
        escrow.statut = 'LIBERE'
        escrow.date_liberation_effective = timezone.now()
        escrow.save(update_fields=['statut', 'date_liberation_effective', 'updated_at'])
        
        logger.info(
            f"Escrow libéré: id={escrow.id}, montant_brut={escrow.montant_bloque}, "
            f"commission={commission}, montant_net={montant_net}, "
            f"beneficiaire={escrow.beneficiaire.id}"
        )
        
        # TODO: Intégrer avec Fedapay pour le transfert réel vers le bénéficiaire
        # Pour l'instant, on enregistre simplement la libération
        
        return {
            "success": True,
            "escrow_id": escrow.id,
            "montant_brut": float(escrow.montant_bloque),
            "commission": float(commission),
            "montant_net": float(montant_net),
            "beneficiaire_id": escrow.beneficiaire.id,
            "date_liberation": escrow.date_liberation_effective.isoformat()
        }
    
    @staticmethod
    def refund_escrow(escrow_id: int, raison: str = "") -> Dict[str, any]:
        """
        Rembourser un paiement en escrow au payeur
        
        Args:
            escrow_id: ID du compte escrow
            raison: Raison du remboursement
            
        Returns:
            Dict avec les détails du remboursement
            
        Raises:
            ValueError: Si l'escrow n'existe pas ou n'est pas en statut BLOQUE
        """
        from .models import EscrowAccount
        from django.utils import timezone
        
        try:
            escrow = EscrowAccount.objects.select_related(
                'transaction', 'transaction__utilisateur'
            ).get(id=escrow_id)
        except EscrowAccount.DoesNotExist:
            raise ValueError(f"Compte escrow {escrow_id} introuvable")
        
        if escrow.statut != 'BLOQUE':
            raise ValueError(
                f"Le compte escrow {escrow_id} n'est pas en statut BLOQUE "
                f"(statut actuel: {escrow.statut})"
            )
        
        # Mettre à jour le statut de l'escrow
        escrow.statut = 'REMBOURSE'
        escrow.date_liberation_effective = timezone.now()
        escrow.save(update_fields=['statut', 'date_liberation_effective', 'updated_at'])
        
        # Mettre à jour le statut de la transaction
        escrow.transaction.statut = 'REFUNDED'
        escrow.transaction.save(update_fields=['statut', 'updated_at'])
        
        logger.info(
            f"Escrow remboursé: id={escrow.id}, montant={escrow.montant_bloque}, "
            f"payeur={escrow.transaction.utilisateur.id}, raison={raison}"
        )
        
        # TODO: Intégrer avec Fedapay pour le remboursement réel
        
        return {
            "success": True,
            "escrow_id": escrow.id,
            "montant_rembourse": float(escrow.montant_bloque),
            "payeur_id": escrow.transaction.utilisateur.id,
            "date_remboursement": escrow.date_liberation_effective.isoformat(),
            "raison": raison
        }
    
    @staticmethod
    def get_escrow_by_transaction(transaction_id: str):
        """
        Récupérer le compte escrow associé à une transaction
        
        Args:
            transaction_id: ID de la transaction
            
        Returns:
            Instance EscrowAccount ou None
        """
        from .models import EscrowAccount
        
        try:
            return EscrowAccount.objects.get(transaction_id=transaction_id)
        except EscrowAccount.DoesNotExist:
            return None
