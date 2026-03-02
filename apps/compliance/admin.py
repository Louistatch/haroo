"""
Interface d'administration pour la conformité
"""
from django.contrib import admin
from .models import (
    CGUAcceptance,
    ElectronicReceipt,
    DataRetentionPolicy,
    AccountDeletionRequest
)


@admin.register(CGUAcceptance)
class CGUAcceptanceAdmin(admin.ModelAdmin):
    """Administration des acceptations CGU"""
    list_display = ['user', 'version_cgu', 'accepted_at', 'ip_address']
    list_filter = ['version_cgu', 'accepted_at']
    search_fields = ['user__username', 'user__email', 'ip_address']
    readonly_fields = ['user', 'version_cgu', 'ip_address', 'user_agent', 'accepted_at']
    date_hierarchy = 'accepted_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ElectronicReceipt)
class ElectronicReceiptAdmin(admin.ModelAdmin):
    """Administration des reçus électroniques"""
    list_display = ['receipt_number', 'buyer_name', 'total_amount', 'issued_at']
    list_filter = ['issued_at']
    search_fields = ['receipt_number', 'buyer_name', 'buyer_phone']
    readonly_fields = [
        'transaction', 'receipt_number', 'buyer_name', 'buyer_phone',
        'description', 'amount', 'tax_amount', 'total_amount', 'issued_at'
    ]
    date_hierarchy = 'issued_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Ne pas permettre la suppression (rétention 10 ans)
        return False


@admin.register(DataRetentionPolicy)
class DataRetentionPolicyAdmin(admin.ModelAdmin):
    """Administration des politiques de rétention"""
    list_display = ['data_type', 'retention_period_days', 'is_active', 'updated_at']
    list_filter = ['data_type', 'is_active']
    search_fields = ['data_type', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('data_type', 'retention_period_days', 'is_active')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AccountDeletionRequest)
class AccountDeletionRequestAdmin(admin.ModelAdmin):
    """Administration des demandes de suppression de compte"""
    list_display = ['user', 'status', 'requested_at', 'processed_at', 'processed_by']
    list_filter = ['status', 'requested_at', 'processed_at']
    search_fields = ['user__username', 'user__email', 'reason']
    readonly_fields = ['user', 'requested_at', 'processed_at', 'processed_by', 'data_export_file']
    date_hierarchy = 'requested_at'
    
    fieldsets = (
        ('Informations de la demande', {
            'fields': ('user', 'reason', 'status')
        }),
        ('Traitement', {
            'fields': ('processed_by', 'processed_at')
        }),
        ('Export des données', {
            'fields': ('data_export_file',)
        }),
        ('Dates', {
            'fields': ('requested_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False
