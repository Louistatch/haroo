"""
Services pour la gestion des paiements via FedaPay (REST API directe)
Docs: https://docs.fedapay.com/api-reference/
Sandbox: https://sandbox-api.fedapay.com/v1
Live:    https://api.fedapay.com/v1

Modes Mobile Money Togo:
  - moov_tg  : Moov Togo
  - togocel  : Togocel T-Money

Numéros de test sandbox:
  - 64000001, 66000001 → succès
  - tout autre numéro  → échec
"""
import hmac
import hashlib
import time
import requests
import logging
from decimal import Decimal
from typing import Dict, Optional

from django.conf import settings
from .models import Transaction

logger = logging.getLogger(__name__)

FEDAPAY_SANDBOX_URL = "https://sandbox-api.fedapay.com/v1"
FEDAPAY_LIVE_URL = "https://api.fedapay.com/v1"

# Modes de paiement Mobile Money supportés
MOBILE_MONEY_MODES = {
    'moov_tg': 'Moov Togo',
    'togocel': 'Togocel T-Money',
    'mtn_open': 'MTN Mobile Money Bénin',
    'moov': 'Moov Bénin',
    'mtn_ci': 'MTN Côte d\'Ivoire',
    'free_sn': 'Free Sénégal',
    'airtel_ne': 'Airtel Niger',
}

# Modes par défaut pour le Togo
TOGO_MODES = ['moov_tg', 'togocel']


class FedapayService:
    """
    Service d'intégration avec l'API FedaPay pour les paiements mobiles.
    Utilise la clé secrète (sk_*) pour les appels serveur.
    La clé publique (pk_*) est utilisée côté frontend uniquement.
    """

    def __init__(self):
        # Utiliser FEDAPAY_SECRET_KEY pour les appels API serveur
        # Fallback sur FEDAPAY_API_KEY pour compatibilité
        self.secret_key = getattr(settings, 'FEDAPAY_SECRET_KEY', '') or \
                          getattr(settings, 'FEDAPAY_API_KEY', '')
        env = getattr(settings, 'FEDAPAY_ENVIRONMENT', 'sandbox')
        self.base_url = FEDAPAY_LIVE_URL if env == 'live' else FEDAPAY_SANDBOX_URL
        self.environment = env
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    # ── HTTP helpers ──

    def _post(self, path: str, payload: dict = None) -> dict:
        resp = requests.post(
            f"{self.base_url}{path}",
            json=payload or {},
            headers=self.headers,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def _get(self, path: str, params: dict = None) -> dict:
        resp = requests.get(
            f"{self.base_url}{path}",
            params=params,
            headers=self.headers,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    # ── Transactions ──

    def initiate_payment(
        self,
        transaction: Transaction,
        callback_url: str,
        description: str = "",
    ) -> Dict[str, any]:
        """
        Créer une transaction FedaPay et retourner l'URL de paiement.
        Flow: create transaction → generate token → return checkout URL.
        """
        try:
            user = transaction.utilisateur
            phone = str(getattr(user, 'phone_number', '') or '').replace('+', '')

            payload = {
                "description": description or f"Paiement {transaction.get_type_transaction_display()}",
                "amount": int(transaction.montant),
                "currency": {"iso": "XOF"},
                "callback_url": callback_url,
                "customer": {
                    "firstname": user.first_name or "Client",
                    "lastname": user.last_name or "Haroo",
                    "email": user.email or f"user{user.id}@haroo.tg",
                    "phone_number": {
                        "number": phone or "90000000",
                        "country": "tg",
                    },
                },
                "custom_metadata": {
                    "transaction_id": str(transaction.id),
                    "user_id": str(user.id),
                    "type": transaction.type_transaction,
                },
            }

            # 1. Créer la transaction FedaPay
            txn_data = self._post("/transactions", payload)
            txn_obj = txn_data.get("v1/transaction", txn_data)
            fedapay_id = str(txn_obj["id"])

            # 2. Générer le token de paiement
            token_data = self._post(f"/transactions/{fedapay_id}/token", {})
            token_str = token_data.get("token", "")
            pay_url = token_data.get("url", "")

            # 3. Persister l'ID FedaPay
            transaction.fedapay_transaction_id = fedapay_id
            transaction.save(update_fields=["fedapay_transaction_id", "updated_at"])

            logger.info(
                "Paiement FedaPay initié: transaction=%s fedapay=%s",
                transaction.id, fedapay_id,
            )

            return {
                "success": True,
                "transaction_id": str(transaction.id),
                "fedapay_transaction_id": fedapay_id,
                "payment_url": pay_url,
                "token": token_str,
            }

        except requests.HTTPError as e:
            body = e.response.text if e.response else str(e)
            logger.error("Erreur HTTP FedaPay: %s — %s", e, body)
            transaction.statut = "FAILED"
            transaction.save(update_fields=["statut", "updated_at"])
            raise Exception(f"Échec FedaPay: {body}")
        except Exception as e:
            logger.error("Erreur initiation paiement: %s", e)
            transaction.statut = "FAILED"
            transaction.save(update_fields=["statut", "updated_at"])
            raise Exception(f"Échec de l'initialisation du paiement: {e}")

    def send_mobile_money(
        self,
        transaction: Transaction,
        mode: str,
        phone_number: str = "",
        callback_url: str = "",
        description: str = "",
    ) -> Dict[str, any]:
        """
        Paiement Mobile Money SANS redirection.
        Crée la transaction, génère le token, puis envoie directement
        la demande de paiement au téléphone du client.

        Args:
            transaction: Transaction Haroo
            mode: moov_tg | togocel | mtn_open | ...
            phone_number: numéro du client (ex: 90123456)
            callback_url: URL de retour optionnelle
            description: description du paiement
        """
        if mode not in MOBILE_MONEY_MODES:
            raise ValueError(f"Mode invalide: {mode}. Modes: {list(MOBILE_MONEY_MODES.keys())}")

        try:
            user = transaction.utilisateur
            phone = phone_number or str(getattr(user, 'phone_number', '') or '').replace('+228', '').replace('+', '')

            # 1. Créer la transaction
            payload = {
                "description": description or f"Paiement {transaction.get_type_transaction_display()}",
                "amount": int(transaction.montant),
                "currency": {"iso": "XOF"},
                "callback_url": callback_url,
                "customer": {
                    "firstname": user.first_name or "Client",
                    "lastname": user.last_name or "Haroo",
                    "email": user.email or f"user{user.id}@haroo.tg",
                    "phone_number": {"number": phone, "country": "tg"},
                },
            }

            txn_data = self._post("/transactions", payload)
            txn_obj = txn_data.get("v1/transaction", txn_data)
            fedapay_id = str(txn_obj["id"])

            # 2. Générer le token
            token_data = self._post(f"/transactions/{fedapay_id}/token", {})
            token_str = token_data.get("token", "")

            # 3. Envoyer le paiement directement (sans redirection)
            self._post(f"/{mode}", {"token": token_str})

            # 4. Persister
            transaction.fedapay_transaction_id = fedapay_id
            transaction.save(update_fields=["fedapay_transaction_id", "updated_at"])

            logger.info(
                "Mobile Money envoyé: transaction=%s fedapay=%s mode=%s phone=%s",
                transaction.id, fedapay_id, mode, phone,
            )

            return {
                "success": True,
                "transaction_id": str(transaction.id),
                "fedapay_transaction_id": fedapay_id,
                "mode": mode,
                "mode_label": MOBILE_MONEY_MODES[mode],
                "message": f"Demande de paiement envoyée sur {phone}. Validez sur votre téléphone.",
            }

        except requests.HTTPError as e:
            body = e.response.text if e.response else str(e)
            logger.error("Erreur Mobile Money FedaPay: %s — %s", e, body)
            transaction.statut = "FAILED"
            transaction.save(update_fields=["statut", "updated_at"])
            raise Exception(f"Échec Mobile Money: {body}")
        except Exception as e:
            logger.error("Erreur Mobile Money: %s", e)
            transaction.statut = "FAILED"
            transaction.save(update_fields=["statut", "updated_at"])
            raise Exception(f"Échec du paiement Mobile Money: {e}")

    def get_transaction_status(self, fedapay_transaction_id: str) -> Dict[str, any]:
        """Récupérer le statut d'une transaction FedaPay."""
        try:
            data = self._get(f"/transactions/{fedapay_transaction_id}")
            txn = data.get("v1/transaction", data)
            return {
                "id": str(txn.get("id")),
                "status": txn.get("status"),
                "amount": txn.get("amount"),
                "currency": txn.get("currency", {}).get("iso", "XOF"),
                "description": txn.get("description"),
                "created_at": txn.get("created_at"),
                "updated_at": txn.get("updated_at"),
            }
        except Exception as e:
            logger.error("Erreur statut FedaPay: %s id=%s", e, fedapay_transaction_id)
            raise

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Vérifier la signature d'un webhook FedaPay.
        Header: X-FEDAPAY-SIGNATURE: t=<timestamp>,s=<hmac_sha256>
        Signed payload: str(timestamp) + '.' + payload
        Tolérance: 300 secondes.
        """
        try:
            webhook_secret = getattr(settings, 'FEDAPAY_WEBHOOK_SECRET', '')
            if not webhook_secret:
                if getattr(settings, 'DEBUG', False):
                    logger.warning("FEDAPAY_WEBHOOK_SECRET absent — vérification ignorée en dev")
                    return True
                else:
                    logger.error("FEDAPAY_WEBHOOK_SECRET absent en production — webhook rejeté")
                    return False

            parts = {}
            for kv in signature.split(','):
                if '=' in kv:
                    k, v = kv.split('=', 1)
                    parts[k.strip()] = v.strip()

            ts_str = parts.get('t', '')
            sig_received = parts.get('s', '')

            if not ts_str or not sig_received:
                logger.warning("Header X-FEDAPAY-SIGNATURE malformé")
                return False

            ts = int(ts_str)
            if abs(time.time() - ts) > 300:
                logger.warning("Webhook FedaPay expiré (timestamp trop ancien)")
                return False

            signed_payload = f"{ts}.{payload}"
            expected = hmac.new(
                webhook_secret.encode('utf-8'),
                signed_payload.encode('utf-8'),
                hashlib.sha256,
            ).hexdigest()

            return hmac.compare_digest(expected, sig_received)

        except Exception as e:
            logger.error("Erreur vérification signature webhook: %s", e)
            return False


class TransactionService:
    """Service pour la gestion des transactions."""

    @staticmethod
    def create_transaction(
        utilisateur,
        type_transaction: str,
        montant: Decimal,
        reference_externe: Optional[str] = None,
    ) -> Transaction:
        commission = TransactionService._calculate_commission(type_transaction, montant)
        transaction = Transaction.objects.create(
            utilisateur=utilisateur,
            type_transaction=type_transaction,
            montant=montant,
            commission_plateforme=commission,
            reference_externe=reference_externe,
            statut="PENDING",
        )
        logger.info(
            "Transaction créée: id=%s type=%s montant=%s commission=%s",
            transaction.id, type_transaction, montant, commission,
        )
        return transaction

    @staticmethod
    def _calculate_commission(type_transaction: str, montant: Decimal) -> Decimal:
        rates = {
            "ACHAT_DOCUMENT": 0,
            "RECRUTEMENT_AGRONOME": settings.COMMISSION_AGRONOME,
            "PREVENTE": settings.COMMISSION_PREVENTE,
            "TRANSPORT": settings.COMMISSION_TRANSPORT,
            "ABONNEMENT": 0,
        }
        rate = rates.get(type_transaction, 0)
        commission = (montant * Decimal(rate)) / Decimal(100)
        return commission.quantize(Decimal("0.01"))

    @staticmethod
    def update_transaction_status(
        transaction: Transaction,
        new_status: str,
        fedapay_data: Optional[Dict] = None,
    ) -> Transaction:
        old_status = transaction.statut
        transaction.statut = new_status
        transaction.save(update_fields=["statut", "updated_at"])
        logger.info(
            "Statut transaction: id=%s %s → %s",
            transaction.id, old_status, new_status,
        )
        return transaction


class CommissionCalculator:
    """Service pour le calcul des commissions."""

    @staticmethod
    def get_commission_rate(type_transaction: str) -> int:
        rates = {
            "ACHAT_DOCUMENT": 0,
            "RECRUTEMENT_AGRONOME": settings.COMMISSION_AGRONOME,
            "PREVENTE": settings.COMMISSION_PREVENTE,
            "TRANSPORT": settings.COMMISSION_TRANSPORT,
            "ABONNEMENT": 0,
        }
        return rates.get(type_transaction, 0)

    @staticmethod
    def calculate_net_amount(montant: Decimal, commission: Decimal) -> Decimal:
        return (montant - commission).quantize(Decimal("0.01"))


class EscrowService:
    """Service pour la gestion des paiements en escrow (séquestre)."""

    @staticmethod
    def create_escrow(transaction, beneficiaire, montant_bloque: Decimal, date_liberation_prevue):
        from .models import EscrowAccount

        escrow = EscrowAccount.objects.create(
            transaction=transaction,
            montant_bloque=montant_bloque,
            beneficiaire=beneficiaire,
            statut="BLOQUE",
            date_liberation_prevue=date_liberation_prevue,
        )
        logger.info(
            "Escrow créé: id=%s transaction=%s beneficiaire=%s montant=%s",
            escrow.id, transaction.id, beneficiaire.id, montant_bloque,
        )
        return escrow

    @staticmethod
    def release_escrow(escrow_id: int) -> Dict[str, any]:
        from .models import EscrowAccount
        from django.utils import timezone

        try:
            escrow = EscrowAccount.objects.select_related(
                "transaction", "beneficiaire"
            ).get(id=escrow_id)
        except EscrowAccount.DoesNotExist:
            raise ValueError(f"Compte escrow {escrow_id} introuvable")

        if escrow.statut != "BLOQUE":
            raise ValueError(
                f"Le compte escrow {escrow_id} n'est pas en statut BLOQUE "
                f"(statut actuel: {escrow.statut})"
            )

        commission = escrow.transaction.commission_plateforme
        montant_net = CommissionCalculator.calculate_net_amount(escrow.montant_bloque, commission)

        escrow.statut = "LIBERE"
        escrow.date_liberation_effective = timezone.now()
        escrow.save(update_fields=["statut", "date_liberation_effective", "updated_at"])

        logger.info(
            "Escrow libéré: id=%s brut=%s commission=%s net=%s beneficiaire=%s",
            escrow.id, escrow.montant_bloque, commission, montant_net, escrow.beneficiaire.id,
        )

        return {
            "success": True,
            "escrow_id": escrow.id,
            "montant_brut": float(escrow.montant_bloque),
            "commission": float(commission),
            "montant_net": float(montant_net),
            "beneficiaire_id": escrow.beneficiaire.id,
            "date_liberation": escrow.date_liberation_effective.isoformat(),
        }

    @staticmethod
    def refund_escrow(escrow_id: int, raison: str = "") -> Dict[str, any]:
        from .models import EscrowAccount
        from django.utils import timezone

        try:
            escrow = EscrowAccount.objects.select_related(
                "transaction", "transaction__utilisateur"
            ).get(id=escrow_id)
        except EscrowAccount.DoesNotExist:
            raise ValueError(f"Compte escrow {escrow_id} introuvable")

        if escrow.statut != "BLOQUE":
            raise ValueError(
                f"Le compte escrow {escrow_id} n'est pas en statut BLOQUE "
                f"(statut actuel: {escrow.statut})"
            )

        escrow.statut = "REMBOURSE"
        escrow.date_liberation_effective = timezone.now()
        escrow.save(update_fields=["statut", "date_liberation_effective", "updated_at"])

        escrow.transaction.statut = "REFUNDED"
        escrow.transaction.save(update_fields=["statut", "updated_at"])

        logger.info(
            "Escrow remboursé: id=%s montant=%s payeur=%s raison=%s",
            escrow.id, escrow.montant_bloque, escrow.transaction.utilisateur.id, raison,
        )

        return {
            "success": True,
            "escrow_id": escrow.id,
            "montant_rembourse": float(escrow.montant_bloque),
            "payeur_id": escrow.transaction.utilisateur.id,
            "date_remboursement": escrow.date_liberation_effective.isoformat(),
            "raison": raison,
        }

    @staticmethod
    def get_escrow_by_transaction(transaction_id: str):
        from .models import EscrowAccount

        try:
            return EscrowAccount.objects.get(transaction_id=transaction_id)
        except EscrowAccount.DoesNotExist:
            return None
