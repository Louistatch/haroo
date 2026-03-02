from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    ExploitantProfile,
    AgronomeProfile,
    OuvrierProfile,
    AcheteurProfile,
    InstitutionProfile,
    DocumentJustificatif
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'phone_number', 'user_type', 'phone_verified', 'is_active']
    list_filter = ['user_type', 'phone_verified', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'phone_number', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations Haroo', {
            'fields': ('phone_number', 'phone_verified', 'user_type', 'two_factor_enabled')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations Haroo', {
            'fields': ('phone_number', 'user_type')
        }),
    )


@admin.register(ExploitantProfile)
class ExploitantProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'superficie_totale', 'canton_principal', 'statut_verification', 'date_verification']
    list_filter = ['statut_verification', 'canton_principal__prefecture__region']
    search_fields = ['user__username', 'user__email', 'user__phone_number']
    readonly_fields = ['date_verification']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Exploitation', {
            'fields': ('superficie_totale', 'canton_principal', 'coordonnees_gps', 'cultures_actuelles')
        }),
        ('Vérification', {
            'fields': ('statut_verification', 'date_verification')
        }),
    )


@admin.register(AgronomeProfile)
class AgronomeProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'canton_rattachement', 'statut_validation', 'badge_valide', 'note_moyenne', 'nombre_avis']
    list_filter = ['statut_validation', 'badge_valide', 'canton_rattachement__prefecture__region']
    search_fields = ['user__username', 'user__email', 'user__phone_number']
    readonly_fields = ['date_validation', 'note_moyenne', 'nombre_avis']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Profil Professionnel', {
            'fields': ('canton_rattachement', 'specialisations')
        }),
        ('Validation', {
            'fields': ('statut_validation', 'badge_valide', 'date_validation', 'motif_rejet')
        }),
        ('Réputation', {
            'fields': ('note_moyenne', 'nombre_avis')
        }),
    )


@admin.register(DocumentJustificatif)
class DocumentJustificatifAdmin(admin.ModelAdmin):
    list_display = ['agronome_profile', 'type_document', 'nom_fichier', 'uploaded_at']
    list_filter = ['type_document', 'uploaded_at']
    search_fields = ['agronome_profile__user__username', 'nom_fichier']
    readonly_fields = ['uploaded_at']
    
    fieldsets = (
        ('Document', {
            'fields': ('agronome_profile', 'type_document', 'fichier', 'nom_fichier')
        }),
        ('Métadonnées', {
            'fields': ('uploaded_at',)
        }),
    )


@admin.register(OuvrierProfile)
class OuvrierProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'disponible', 'note_moyenne', 'nombre_avis']
    list_filter = ['disponible']
    search_fields = ['user__username', 'user__email', 'user__phone_number']
    readonly_fields = ['note_moyenne', 'nombre_avis']
    filter_horizontal = ['cantons_disponibles']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Profil Professionnel', {
            'fields': ('competences', 'cantons_disponibles', 'disponible')
        }),
        ('Réputation', {
            'fields': ('note_moyenne', 'nombre_avis')
        }),
    )


@admin.register(AcheteurProfile)
class AcheteurProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'type_acheteur', 'volume_achats_annuel']
    list_filter = ['type_acheteur']
    search_fields = ['user__username', 'user__email', 'user__phone_number']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Profil Acheteur', {
            'fields': ('type_acheteur', 'volume_achats_annuel')
        }),
    )


@admin.register(InstitutionProfile)
class InstitutionProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'nom_organisme', 'niveau_acces']
    list_filter = ['niveau_acces']
    search_fields = ['user__username', 'nom_organisme']
    filter_horizontal = ['regions_acces']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Profil Institution', {
            'fields': ('nom_organisme', 'niveau_acces', 'regions_acces')
        }),
    )

