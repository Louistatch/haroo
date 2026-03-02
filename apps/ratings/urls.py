"""
URLs pour le système de notation
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotationViewSet

app_name = 'ratings'

router = DefaultRouter()
router.register(r'', NotationViewSet, basename='notation')

urlpatterns = [
    path('', include(router.urls)),
]
