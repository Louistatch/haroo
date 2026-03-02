"""
Configuration de l'admin pour les missions
"""
from django.contrib import admin
from .models import Mission


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    """Configuration de l'admin pour les missions"""
    list_display = [
        'id', 'exploitant', 'agronome', 'budget_propose',
        'statut', 'created_at'
    ]
    list_filter = ['statut', 'created_at']
    search_fields = [
        'exploitant__first_name', 'exploitant__last_name',
        'agronome__first_name', 'agronome__last_name',
        'description'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('exploitant', 'agronome', 'description', 'budget_propose')
        }),
        ('Statut et dates', {
            'fields': ('statut', 'date_debut', 'date_fin')
        }),
        ('Transaction', {
            'fields': ('transaction',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
