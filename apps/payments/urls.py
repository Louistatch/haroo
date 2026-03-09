"""
URLs pour l'API de paiements
"""
from django.urls import path
from .views import (
    InitiatePaymentView,
    TransactionDetailView,
    TransactionHistoryView,
    FedapayWebhookView,
    PaymentCallbackView,
    MobileMoneyPaymentView,
    TransactionStatusView,
)

app_name = 'payments'

urlpatterns = [
    # Initialisation de paiement (redirection checkout FedaPay)
    path('initiate', InitiatePaymentView.as_view(), name='initiate-payment'),

    # Paiement Mobile Money direct (sans redirection)
    path('mobile-money', MobileMoneyPaymentView.as_view(), name='mobile-money-payment'),

    # Vérifier le statut d'une transaction (polling)
    path('status/<uuid:pk>', TransactionStatusView.as_view(), name='transaction-status'),

    # Détails d'une transaction
    path('transactions/<uuid:pk>', TransactionDetailView.as_view(), name='transaction-detail'),

    # Historique des transactions
    path('transactions/history', TransactionHistoryView.as_view(), name='transaction-history'),

    # Webhook Fedapay
    path('webhooks/fedapay', FedapayWebhookView.as_view(), name='fedapay-webhook'),

    # Callback après paiement
    path('callback', PaymentCallbackView.as_view(), name='payment-callback'),
]
