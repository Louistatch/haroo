from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OffreEmploiViewSet, ContratSaisonnierViewSet,
    AnnonceCollectiveViewSet, AnnonceOuvrierViewSet
)

router = DefaultRouter()
router.register(r'jobs', OffreEmploiViewSet, basename='job')
router.register(r'contrats', ContratSaisonnierViewSet, basename='contrat')
router.register(r'annonces-collectives', AnnonceCollectiveViewSet, basename='annonce-collective')
router.register(r'annonces-ouvriers', AnnonceOuvrierViewSet, basename='annonce-ouvrier')

urlpatterns = [
    path('', include(router.urls)),
]
