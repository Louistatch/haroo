from django.contrib import admin
from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['card_number', 'card_type', 'statut', 'expiry_date', 'created_at']
    list_filter = ['card_type', 'statut']
    search_fields = ['card_number']
    readonly_fields = ['created_at', 'updated_at']
