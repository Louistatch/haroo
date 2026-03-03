from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, PreferenceViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'preferences', PreferenceViewSet, basename='preference-notification')

urlpatterns = [
    path('', include(router.urls)),
]
