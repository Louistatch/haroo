"""
Views pour le découpage administratif du Togo
"""
from django.core.cache import cache
from django.db.models import Q, Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Region, Prefecture, Canton
from .serializers import (
    RegionSerializer, RegionDetailSerializer,
    PrefectureSerializer, PrefectureDetailSerializer,
    CantonSerializer
)


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les régions du Togo
    
    Endpoints:
    - GET /api/v1/regions - Liste toutes les régions (avec cache Redis)
    - GET /api/v1/regions/{id} - Détails d'une région
    - GET /api/v1/regions/{id}/prefectures - Préfectures d'une région
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        """Utiliser le serializer détaillé pour retrieve"""
        if self.action == 'retrieve':
            return RegionDetailSerializer
        return RegionSerializer
    
    def list(self, request, *args, **kwargs):
        """
        Liste toutes les régions avec cache Redis
        Cache key: 'haroo:regions:list'
        TTL: 3600 secondes (1 heure)
        """
        cache_key = 'regions:list'
        
        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
        except Exception:
            # Redis n'est pas disponible, continuer sans cache
            pass
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        
        # Mettre en cache pour 1 heure
        try:
            cache.set(cache_key, data, 3600)
        except Exception:
            # Redis n'est pas disponible, continuer sans cache
            pass
        
        return Response(data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Détails d'une région avec ses préfectures
        Optimisé avec prefetch_related
        """
        cache_key = f'region:detail:{kwargs.get("pk")}'
        
        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
        except Exception:
            # Redis n'est pas disponible, continuer sans cache
            pass
        
        # Optimiser avec prefetch_related pour éviter N+1 queries
        instance = self.get_queryset().prefetch_related('prefectures').get(pk=kwargs.get('pk'))
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Mettre en cache pour 1 heure
        try:
            cache.set(cache_key, data, 3600)
        except Exception:
            # Redis n'est pas disponible, continuer sans cache
            pass
        
        return Response(data)
    
    @action(detail=True, methods=['get'], url_path='prefectures')
    def prefectures(self, request, pk=None):
        """
        Retourne toutes les préfectures d'une région
        GET /api/v1/regions/{id}/prefectures
        """
        cache_key = f'region:{pk}:prefectures'
        
        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
        except Exception:
            # Redis n'est pas disponible, continuer sans cache
            pass
        
        region = self.get_object()
        # Optimiser avec select_related pour inclure la région
        prefectures = Prefecture.objects.filter(region=region).select_related('region')
        serializer = PrefectureSerializer(prefectures, many=True)
        data = serializer.data
        
        # Mettre en cache pour 1 heure
        try:
            cache.set(cache_key, data, 3600)
        except Exception:
            # Redis n'est pas disponible, continuer sans cache
            pass
        
        return Response(data)


class PrefectureViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les préfectures du Togo
    
    Endpoints:
    - GET /api/v1/prefectures - Liste toutes les préfectures
    - GET /api/v1/prefectures?region={id} - Préfectures d'une région
    - GET /api/v1/prefectures/{id} - Détails d'une préfecture
    - GET /api/v1/prefectures/{id}/cantons - Cantons d'une préfecture
    """
    queryset = Prefecture.objects.select_related('region').all()
    serializer_class = PrefectureSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        qs = super().get_queryset()
        region = self.request.query_params.get('region')
        if region:
            qs = qs.filter(region_id=region)
        return qs
    
    def get_serializer_class(self):
        """Utiliser le serializer détaillé pour retrieve"""
        if self.action == 'retrieve':
            return PrefectureDetailSerializer
        return PrefectureSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """
        Détails d'une préfecture avec ses cantons
        Optimisé avec select_related et prefetch_related
        """
        cache_key = f'prefecture:detail:{kwargs.get("pk")}'
        
        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
        except Exception:
            # Redis n'est pas disponible, continuer sans cache
            pass
        
        # Optimiser avec select_related et prefetch_related
        instance = self.get_queryset().prefetch_related('cantons').get(pk=kwargs.get('pk'))
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Mettre en cache pour 1 heure
        try:
            cache.set(cache_key, data, 3600)
        except Exception:
            # Redis n'est pas disponible, continuer sans cache
            pass
        
        return Response(data)
    
    @action(detail=True, methods=['get'], url_path='cantons')
    def cantons(self, request, pk=None):
        """
        Retourne tous les cantons d'une préfecture
        GET /api/v1/prefectures/{id}/cantons
        """
        cache_key = f'prefecture:{pk}:cantons'
        
        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
        except Exception:
            # Redis n'est pas disponible, continuer sans cache
            pass
        
        prefecture = self.get_object()
        # Optimiser avec select_related pour inclure prefecture et region
        cantons = Canton.objects.filter(
            prefecture=prefecture
        ).select_related('prefecture', 'prefecture__region')
        
        serializer = CantonSerializer(cantons, many=True)
        data = serializer.data
        
        # Mettre en cache pour 1 heure
        try:
            cache.set(cache_key, data, 3600)
        except Exception:
            # Redis n'est pas disponible, continuer sans cache
            pass
        
        return Response(data)


class CantonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les cantons du Togo
    
    Endpoints:
    - GET /api/v1/cantons - Liste tous les cantons
    - GET /api/v1/cantons?prefecture={id} - Cantons d'une préfecture
    - GET /api/v1/cantons/{id} - Détails d'un canton
    - GET /api/v1/cantons/search?q={query} - Recherche full-text de cantons
    """
    queryset = Canton.objects.select_related('prefecture', 'prefecture__region').all()
    serializer_class = CantonSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        qs = super().get_queryset()
        prefecture = self.request.query_params.get('prefecture')
        if prefecture:
            qs = qs.filter(prefecture_id=prefecture)
        return qs
    
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Recherche full-text de cantons par nom
        GET /api/v1/cantons/search?q={query}
        
        Exigence: Retourner les résultats en moins de 500ms
        """
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response(
                {'error': 'Le paramètre "q" est requis pour la recherche'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier le cache pour cette recherche
        cache_key = f'canton:search:{query.lower()}'
        
        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
        except Exception:
            # Redis n'est pas disponible, continuer sans cache
            pass
        
        # Recherche full-text avec icontains (insensible à la casse)
        # Optimisé avec select_related pour éviter N+1 queries
        cantons = self.get_queryset().filter(
            Q(nom__icontains=query) | Q(code__icontains=query)
        )
        
        serializer = self.get_serializer(cantons, many=True)
        data = serializer.data
        
        # Mettre en cache pour 30 minutes
        try:
            cache.set(cache_key, data, 1800)
        except Exception:
            # Redis n'est pas disponible, continuer sans cache
            pass
        
        return Response(data)
