from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'utilisateur', 'type_transaction', 'montant', 'statut', 'created_at']
    list_filter = ['statut', 'type_transaction', 'created_at']
    search_fields = ['id', 'utilisateur__username', 'fedapay_transaction_id', 'reference_externe']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
