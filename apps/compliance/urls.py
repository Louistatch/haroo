"""
URLs pour la conformité réglementaire
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'compliance'

router = DefaultRouter()
router.register(r'cgu-acceptances', views.CGUAcceptanceViewSet, basename='cgu-acceptance')
router.register(r'receipts', views.ElectronicReceiptViewSet, basename='receipt')
router.register(r'account-deletion', views.AccountDeletionViewSet, basename='account-deletion')
router.register(r'retention-policies', views.DataRetentionPolicyViewSet, basename='retention-policy')

urlpatterns = [
    # Pages publiques
    path('cgu/', views.cgu_view, name='cgu'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy-policy'),
    
    # Export des données
    path('data-export/', views.DataExportView.as_view(), name='data-export'),
    
    # Routes du router
    path('', include(router.urls)),
]
