"""
URLs pour les documents techniques
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentTechniqueViewSet, PurchaseHistoryViewSet

router = DefaultRouter()
router.register(r'documents', DocumentTechniqueViewSet, basename='document')
router.register(r'purchases/history', PurchaseHistoryViewSet, basename='purchase-history')

urlpatterns = [
    path('', include(router.urls)),
]
