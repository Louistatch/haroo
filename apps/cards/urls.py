from django.urls import path
from .views import CardVerifyView

urlpatterns = [
    path('verify/<str:card_number>/', CardVerifyView.as_view(), name='card-verify'),
]
