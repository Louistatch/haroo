"""
Vues pour l'API de paiements
"""
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import logging

from .models import Transaction
from .serializers import (
    InitiatePaymentSerializer,
    PaymentResponseSerializer,
    TransactionSerializer,
    TransactionHistorySerializer,
    WebhookPayloadSerializer,
    MobileMoneyPaymentSerializer,
)
from .services import FedapayService, TransactionService
from .post_payment_actions import PostPaymentActionHandler

logger = logging.getLogger(__name__)


class InitiatePaymentView(APIView):
    """
    POST /api/v1/payments/initiate
    
    Initier un paiement via Fedapay
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Créer une transaction et rediriger vers Fedapay
        
        Body:
        {
            "type_transaction": "ACHAT_DOCUMENT",
            "montant": 5000.00,
            "reference_externe": "doc_123",
            "description": "Achat document technique",
            "callback_url": "https://example.com/callback"  # optionnel
        }
        
        Returns:
        {
            "success": true,
            "transaction_id": "uuid",
            "fedapay_transaction_id": "fedapay_id",
            "payment_url": "https://checkout.fedapay.com/...",
            "token": "token",
            "message": "Redirection vers Fedapay"
        }
        """
        serializer = InitiatePaymentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Créer la transaction
            transaction = TransactionService.create_transaction(
                utilisateur=request.user,
                type_transaction=serializer.validated_data['type_transaction'],
                montant=serializer.validated_data['montant'],
                reference_externe=serializer.validated_data.get('reference_externe')
            )
            
            # Déterminer l'URL de callback (redirection frontend après paiement)
            callback_url = serializer.validated_data.get('callback_url')
            if not callback_url:
                from django.conf import settings as django_settings
                frontend_url = getattr(django_settings, 'FRONTEND_URL', 'http://localhost:5000')
                callback_url = f"{frontend_url.rstrip('/')}/payment/success"
            
            # Initialiser le paiement Fedapay
            fedapay_service = FedapayService()
            payment_data = fedapay_service.initiate_payment(
                transaction=transaction,
                callback_url=callback_url,
                description=serializer.validated_data.get('description', '')
            )
            
            # Ajouter un message
            payment_data['message'] = "Redirection vers Fedapay pour finaliser le paiement"
            
            return Response(
                payment_data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du paiement: {str(e)}")
            return Response(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Échec de l'initialisation du paiement"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransactionDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/transactions/{id}
    
    Récupérer les détails d'une transaction
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    
    def get_queryset(self):
        """Filtrer pour que l'utilisateur ne voie que ses propres transactions"""
        return Transaction.objects.filter(utilisateur=self.request.user)


class TransactionHistoryView(generics.ListAPIView):
    """
    GET /api/v1/transactions/history
    
    Récupérer l'historique des transactions de l'utilisateur
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionHistorySerializer
    
    def get_queryset(self):
        """Filtrer les transactions de l'utilisateur connecté"""
        queryset = Transaction.objects.filter(utilisateur=self.request.user)
        
        # Filtres optionnels
        type_transaction = self.request.query_params.get('type')
        statut = self.request.query_params.get('statut')
        
        if type_transaction:
            queryset = queryset.filter(type_transaction=type_transaction)
        
        if statut:
            queryset = queryset.filter(statut=statut)
        
        return queryset.order_by('-created_at')


@method_decorator(csrf_exempt, name='dispatch')
class FedapayWebhookView(APIView):
    """
    POST /api/v1/payments/webhooks/fedapay
    
    Recevoir les webhooks de Fedapay pour mettre à jour le statut des transactions
    """
    permission_classes = []  # Pas d'authentification pour les webhooks
    
    def post(self, request):
        """
        Traiter un webhook Fedapay
        
        Body (exemple):
        {
            "event": "transaction.approved",
            "entity": {
                "id": "fedapay_transaction_id",
                "status": "approved",
                "amount": 5000,
                ...
            }
        }
        """
        try:
            # Vérifier la signature du webhook
            signature = request.headers.get('X-Fedapay-Signature', '')
            payload = request.body.decode('utf-8')
            
            fedapay_service = FedapayService()
            if not fedapay_service.verify_webhook_signature(payload, signature):
                logger.warning("Signature webhook Fedapay invalide")
                return Response(
                    {"error": "Signature invalide"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Valider les données du webhook
            data = json.loads(payload)
            serializer = WebhookPayloadSerializer(data=data)
            
            if not serializer.is_valid():
                logger.error(f"Données webhook invalides: {serializer.errors}")
                return Response(
                    {"error": "Données invalides"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Extraire les informations
            event = serializer.validated_data['event']
            entity = serializer.validated_data['entity']
            fedapay_transaction_id = str(entity.get('id'))
            
            # Trouver la transaction correspondante
            try:
                transaction = Transaction.objects.get(
                    fedapay_transaction_id=fedapay_transaction_id
                )
            except Transaction.DoesNotExist:
                logger.error(
                    f"Transaction non trouvée pour fedapay_id: {fedapay_transaction_id}"
                )
                return Response(
                    {"error": "Transaction non trouvée"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Mettre à jour le statut selon l'événement
            if event == 'transaction.approved':
                new_status = 'SUCCESS'
            elif event in ['transaction.canceled', 'transaction.failed']:
                new_status = 'FAILED'
            else:
                new_status = transaction.statut
            
            # Mettre à jour la transaction
            TransactionService.update_transaction_status(
                transaction=transaction,
                new_status=new_status,
                fedapay_data=entity
            )
            
            logger.info(
                f"Webhook traité: event={event}, transaction_id={transaction.id}, "
                f"new_status={new_status}"
            )
            
            # Déclencher les actions post-paiement si le paiement est réussi
            if new_status == 'SUCCESS':
                action_success = PostPaymentActionHandler.handle_successful_payment(transaction)
                if not action_success:
                    logger.warning(
                        f"Les actions post-paiement ont échoué pour transaction_id={transaction.id}"
                    )
            
            return Response(
                {"success": True, "message": "Webhook traité avec succès"},
                status=status.HTTP_200_OK
            )
            
        except json.JSONDecodeError:
            logger.error("Erreur de décodage JSON du webhook")
            return Response(
                {"error": "Format JSON invalide"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erreur lors du traitement du webhook: {str(e)}")
            return Response(
                {"error": "Erreur interne du serveur"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentCallbackView(APIView):
    """
    GET /api/v1/payments/callback
    
    Page de retour après paiement Fedapay (pour l'utilisateur)
    """
    permission_classes = []  # Accessible sans authentification
    
    def get(self, request):
        """
        Afficher le résultat du paiement à l'utilisateur
        
        Query params:
        - transaction_id: ID de la transaction Fedapay
        - status: Statut du paiement
        """
        fedapay_transaction_id = request.query_params.get('transaction_id')
        payment_status = request.query_params.get('status')
        
        if not fedapay_transaction_id:
            return Response(
                {
                    "success": False,
                    "message": "ID de transaction manquant"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Trouver la transaction
            transaction = Transaction.objects.get(
                fedapay_transaction_id=fedapay_transaction_id
            )
            
            return Response(
                {
                    "success": True,
                    "transaction_id": str(transaction.id),
                    "statut": transaction.statut,
                    "statut_display": transaction.get_statut_display(),
                    "montant": str(transaction.montant),
                    "type": transaction.get_type_transaction_display(),
                    "message": self._get_status_message(transaction.statut)
                },
                status=status.HTTP_200_OK
            )
            
        except Transaction.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Transaction non trouvée"
                },
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _get_status_message(self, statut: str) -> str:
        """Obtenir un message convivial selon le statut"""
        messages = {
            'PENDING': "Votre paiement est en cours de traitement",
            'SUCCESS': "Votre paiement a été effectué avec succès",
            'FAILED': "Votre paiement a échoué. Veuillez réessayer",
            'REFUNDED': "Votre paiement a été remboursé"
        }
        return messages.get(statut, "Statut inconnu")


class MobileMoneyPaymentView(APIView):
    """
    POST /api/v1/payments/mobile-money

    Paiement Mobile Money direct (sans redirection vers FedaPay checkout).
    Envoie une demande de paiement directement sur le téléphone du client.
    Modes Togo: moov_tg, togocel
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MobileMoneyPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            data = serializer.validated_data
            transaction = TransactionService.create_transaction(
                utilisateur=request.user,
                type_transaction=data["type_transaction"],
                montant=data["montant"],
                reference_externe=data.get("reference_externe"),
            )

            frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5000")
            callback_url = f"{frontend_url.rstrip('/')}/payment/success"

            fedapay_service = FedapayService()
            result = fedapay_service.send_mobile_money(
                transaction=transaction,
                mode=data["mode"],
                phone_number=data["phone_number"],
                callback_url=callback_url,
                description=data.get("description", ""),
            )

            return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error("Erreur Mobile Money: %s", e)
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TransactionStatusView(APIView):
    """
    GET /api/v1/payments/status/<transaction_id>

    Vérifier le statut d'une transaction (polling côté frontend).
    Interroge FedaPay si la transaction est encore PENDING.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            transaction = Transaction.objects.get(pk=pk, utilisateur=request.user)
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction non trouvée"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Si PENDING et qu'on a un ID FedaPay, vérifier le statut en temps réel
        if transaction.statut == "PENDING" and transaction.fedapay_transaction_id:
            try:
                fedapay_service = FedapayService()
                fedapay_status = fedapay_service.get_transaction_status(
                    transaction.fedapay_transaction_id
                )
                status_map = {
                    "approved": "SUCCESS",
                    "declined": "FAILED",
                    "canceled": "FAILED",
                    "refunded": "REFUNDED",
                }
                new_status = status_map.get(fedapay_status.get("status"), "PENDING")
                if new_status != "PENDING":
                    TransactionService.update_transaction_status(transaction, new_status)
                    if new_status == "SUCCESS":
                        PostPaymentActionHandler.handle_successful_payment(transaction)
            except Exception as e:
                logger.warning("Impossible de vérifier le statut FedaPay: %s", e)

        return Response({
            "transaction_id": str(transaction.id),
            "statut": transaction.statut,
            "statut_display": transaction.get_statut_display(),
            "montant": str(transaction.montant),
            "type": transaction.get_type_transaction_display(),
            "fedapay_transaction_id": transaction.fedapay_transaction_id,
        })
