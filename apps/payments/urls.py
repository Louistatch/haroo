"""
URLs pour l'API de paiements
"""
from django.urls import path
from .views import (
    InitiatePaymentView,
    TransactionDetailView,
    TransactionHistoryView,
    FedapayWebhookView,
    PaymentCallbackView
)

app_name = 'payments'

urlpatterns = [
    # Initialisation de paiement
    path('initiate', InitiatePaymentView.as_view(), name='initiate-payment'),
    
    # Détails d'une transaction
    path('transactions/<uuid:pk>', TransactionDetailView.as_view(), name='transaction-detail'),
    
    # Historique des transactions
    path('transactions/history', TransactionHistoryView.as_view(), name='transaction-history'),
    
    # Webhook Fedapay
    path('webhooks/fedapay', FedapayWebhookView.as_view(), name='fedapay-webhook'),
    
    # Callback après paiement
    path('callback', PaymentCallbackView.as_view(), name='payment-callback'),
]
