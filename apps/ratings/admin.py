"""
Interface d'administration pour le système de notation
"""
from django.contrib import admin
from .models import Notation, SignalementNotation
from .services import ModerationService


@admin.register(Notation)
class NotationAdmin(admin.ModelAdmin):
    """Administration des notations"""
    list_display = [
        'id',
        'notateur',
        'note',
        'note_valeur',
        'statut',
        'nombre_signalements',
        'created_at'
    ]
    list_filter = ['statut', 'note_valeur', 'created_at']
    search_fields = [
        'notateur__first_name',
        'notateur__last_name',
        'note__first_name',
        'note__last_name',
        'commentaire'
    ]
    readonly_fields = ['created_at', 'updated_at', 'nombre_signalements']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('notateur', 'note', 'note_valeur', 'commentaire')
        }),
        ('Référence', {
            'fields': ('mission',)
        }),
        ('Modération', {
            'fields': ('statut', 'nombre_signalements')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_notations', 'reject_notations']
    
    def approve_notations(self, request, queryset):
        """Action pour approuver des notations"""
        count = 0
        for notation in queryset:
            ModerationService.approve_notation(notation)
            count += 1
        
        self.message_user(
            request,
            f"{count} notation(s) approuvée(s) avec succès"
        )
    approve_notations.short_description = "Approuver les notations sélectionnées"
    
    def reject_notations(self, request, queryset):
        """Action pour rejeter des notations"""
        count = 0
        for notation in queryset:
            ModerationService.reject_notation(notation)
            count += 1
        
        self.message_user(
            request,
            f"{count} notation(s) rejetée(s) avec succès"
        )
    reject_notations.short_description = "Rejeter les notations sélectionnées"


@admin.register(SignalementNotation)
class SignalementNotationAdmin(admin.ModelAdmin):
    """Administration des signalements"""
    list_display = [
        'id',
        'notation',
        'signaleur',
        'motif',
        'traite',
        'created_at'
    ]
    list_filter = ['motif', 'traite', 'created_at']
    search_fields = [
        'signaleur__first_name',
        'signaleur__last_name',
        'description'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('notation', 'signaleur', 'motif', 'description')
        }),
        ('Traitement', {
            'fields': ('traite',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
