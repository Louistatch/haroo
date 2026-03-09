from django.contrib import admin
from .models import OffreEmploiSaisonnier, ContratSaisonnier, HeuresTravaillees


@admin.register(OffreEmploiSaisonnier)
class OffreEmploiSaisonnierAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_travail', 'exploitant', 'canton', 'date_debut', 'date_fin', 'statut')
    list_filter = ('statut', 'canton')
    search_fields = ('type_travail', 'description', 'exploitant__email', 'exploitant__first_name', 'exploitant__last_name')


@admin.register(ContratSaisonnier)
class ContratSaisonnierAdmin(admin.ModelAdmin):
    list_display = ('id', 'offre', 'ouvrier', 'exploitant', 'statut')
    list_filter = ('statut',)
    search_fields = ('ouvrier__email', 'exploitant__email', 'offre__type_travail')


@admin.register(HeuresTravaillees)
class HeuresTravailleesAdmin(admin.ModelAdmin):
    list_display = ('id', 'contrat', 'date', 'heures', 'statut_validation', 'montant_calcule')
    list_filter = ('statut_validation', 'date')
    search_fields = ('contrat__ouvrier__email', 'contrat__exploitant__email')

from .models import AnnonceCollective, ParticipationAnnonce


class ParticipationInline(admin.TabularInline):
    model = ParticipationAnnonce
    extra = 0
    readonly_fields = ('exploitant', 'superficie_apportee', 'created_at')


@admin.register(AnnonceCollective)
class AnnonceCollectiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_travail', 'createur', 'canton', 'superficie_cumulee', 'seuil_hectares', 'statut', 'date_expiration')
    list_filter = ('statut', 'canton')
    search_fields = ('type_travail', 'description', 'createur__email', 'createur__first_name')
    inlines = [ParticipationInline]
    readonly_fields = ('superficie_cumulee', 'offre_generee')
