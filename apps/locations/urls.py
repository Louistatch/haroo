"""
URLs pour le découpage administratif du Togo
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, PrefectureViewSet, CantonViewSet

# Créer le router pour les ViewSets
router = DefaultRouter()
router.register(r'regions', RegionViewSet, basename='region')
router.register(r'prefectures', PrefectureViewSet, basename='prefecture')
router.register(r'cantons', CantonViewSet, basename='canton')

urlpatterns = [
    path('', include(router.urls)),
]
