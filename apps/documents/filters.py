"""
Filtres pour les documents et achats
"""
import django_filters
from django.db.models import Q
from .models import DocumentTechnique, AchatDocument


class DocumentTechniqueFilter(django_filters.FilterSet):
    """
    Filtres pour les documents techniques
    """
    region = django_filters.NumberFilter(field_name='region__id')
    prefecture = django_filters.NumberFilter(field_name='prefecture__id')
    canton = django_filters.NumberFilter(field_name='canton__id')
    culture = django_filters.CharFilter(field_name='culture', lookup_expr='icontains')
    type = django_filters.CharFilter(field_name='template__type_document')
    prix_min = django_filters.NumberFilter(field_name='prix', lookup_expr='gte')
    prix_max = django_filters.NumberFilter(field_name='prix', lookup_expr='lte')
    
    class Meta:
        model = DocumentTechnique
        fields = ['region', 'prefecture', 'canton', 'culture', 'type', 'prix_min', 'prix_max']


class AchatDocumentFilter(django_filters.FilterSet):
    """
    Filtres pour l'historique des achats
    
    Exigence: 5.3
    """
    # Filtres par date
    date_debut = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Date de début'
    )
    date_fin = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Date de fin'
    )
    
    # Filtre par type de document
    type_document = django_filters.CharFilter(
        field_name='document__template__type_document',
        label='Type de document'
    )
    
    # Filtre par culture
    culture = django_filters.CharFilter(
        field_name='document__culture',
        lookup_expr='icontains',
        label='Culture'
    )
    
    # Filtre par statut de transaction
    statut = django_filters.CharFilter(
        field_name='transaction__statut',
        label='Statut de la transaction'
    )
    
    # Filtre par lien expiré
    lien_expire = django_filters.BooleanFilter(
        method='filter_lien_expire',
        label='Lien expiré'
    )
    
    class Meta:
        model = AchatDocument
        fields = ['date_debut', 'date_fin', 'type_document', 'culture', 'statut', 'lien_expire']
    
    def filter_lien_expire(self, queryset, name, value):
        """
        Filtre les achats selon l'état d'expiration du lien
        """
        from django.utils import timezone
        
        if value:
            # Liens expirés
            return queryset.filter(expiration_lien__lt=timezone.now())
        else:
            # Liens non expirés
            return queryset.filter(expiration_lien__gte=timezone.now())
