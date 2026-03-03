from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OffreEmploiViewSet, ContratSaisonnierViewSet

router = DefaultRouter()
router.register(r'jobs', OffreEmploiViewSet, basename='job')
router.register(r'contrats', ContratSaisonnierViewSet, basename='contrat')

urlpatterns = [
    path('', include(router.urls)),
]
