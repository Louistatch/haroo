from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PreventeViewSet, EngagementViewSet

router = DefaultRouter()
router.register(r'presales', PreventeViewSet, basename='presales')
router.register(r'engagements', EngagementViewSet, basename='engagements')

urlpatterns = [
    path('', include(router.urls)),
]
