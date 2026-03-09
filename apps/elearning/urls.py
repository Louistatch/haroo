from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategorieViewSet, CoursViewSet, InscriptionViewSet, QuizViewSet

router = DefaultRouter()
router.register(r'categories', CategorieViewSet, basename='categorie')
router.register(r'cours', CoursViewSet, basename='cours')
router.register(r'inscriptions', InscriptionViewSet, basename='inscription')
router.register(r'quiz', QuizViewSet, basename='quiz')

urlpatterns = [
    path('', include(router.urls)),
]
