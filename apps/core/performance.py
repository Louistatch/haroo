"""
Utilitaires pour l'optimisation des performances

Ce module fournit des outils pour:
- Optimiser les requêtes database (select_related, prefetch_related)
- Gérer le cache Redis
- Pagination cursor pour grandes listes
- Monitoring des performances
"""
from functools import wraps
from typing import Optional, List, Any, Callable
from django.core.cache import cache
from django.db.models import QuerySet, Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.pagination import CursorPagination
import time
import logging

logger = logging.getLogger('performance')


# ============================================================================
# OPTIMISATION DES REQUÊTES DATABASE
# ============================================================================

class QueryOptimizer:
    """
    Classe utilitaire pour optimiser les requêtes database
    
    Utilise select_related() pour ForeignKey et prefetch_related() pour ManyToMany
    afin d'éliminer les requêtes N+1.
    """
    
    @staticmethod
    def optimize_user_queryset(queryset: QuerySet) -> QuerySet:
        """
        Optimise un queryset de User avec toutes les relations
        
        Args:
            queryset: QuerySet de User
            
        Returns:
            QuerySet optimisé avec select_related et prefetch_related
        """
        return queryset.select_related(
            'exploitantprofile',
            'agronomeprofile',
            'ouvrierprofile',
            'acheteurprofile',
            'institutionprofile'
        ).prefetch_related(
            'documentjustificatif_set',
            'farmverificationdocument_set'
        )
    
    @staticmethod
    def optimize_agronomist_queryset(queryset: QuerySet) -> QuerySet:
        """
        Optimise un queryset d'AgronomeProfile
        
        Args:
            queryset: QuerySet d'AgronomeProfile
            
        Returns:
            QuerySet optimisé
        """
        return queryset.select_related(
            'user'
        ).prefetch_related(
            Prefetch(
                'user__documentjustificatif_set',
                queryset=None  # Tous les documents
            )
        )
    
    @staticmethod
    def optimize_exploitant_queryset(queryset: QuerySet) -> QuerySet:
        """
        Optimise un queryset d'ExploitantProfile
        
        Args:
            queryset: QuerySet d'ExploitantProfile
            
        Returns:
            QuerySet optimisé
        """
        return queryset.select_related(
            'user',
            'location'
        ).prefetch_related(
            'user__farmverificationdocument_set'
        )
    
    @staticmethod
    def count_queries(func: Callable) -> Callable:
        """
        Décorateur pour compter le nombre de requêtes SQL
        
        Usage:
            @QueryOptimizer.count_queries
            def my_view(request):
                ...
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            from django.db import connection, reset_queries
            from django.conf import settings
            
            # Activer le debug temporairement
            old_debug = settings.DEBUG
            settings.DEBUG = True
            reset_queries()
            
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            num_queries = len(connection.queries)
            duration = end_time - start_time
            
            logger.info(
                f"Function: {func.__name__} | "
                f"Queries: {num_queries} | "
                f"Duration: {duration:.3f}s"
            )
            
            # Restaurer le debug
            settings.DEBUG = old_debug
            
            return result
        return wrapper


# ============================================================================
# CACHE REDIS
# ============================================================================

class CacheManager:
    """
    Gestionnaire de cache Redis avec invalidation automatique
    
    Fournit des méthodes pour:
    - Mettre en cache des données
    - Invalider le cache automatiquement
    - Configurer des TTL par type de données
    """
    
    # TTL par défaut (en secondes)
    TTL_SHORT = 300  # 5 minutes
    TTL_MEDIUM = 3600  # 1 heure
    TTL_LONG = 86400  # 24 heures
    
    # Préfixes de clés
    PREFIX_USER = "user"
    PREFIX_AGRONOMIST = "agronomist"
    PREFIX_LOCATION = "location"
    PREFIX_DOCUMENT = "document"
    PREFIX_LIST = "list"
    
    @classmethod
    def _make_key(cls, prefix: str, identifier: Any) -> str:
        """Génère une clé de cache"""
        return f"{prefix}:{identifier}"
    
    @classmethod
    def get_or_set(
        cls,
        key: str,
        callback: Callable,
        ttl: int = TTL_MEDIUM
    ) -> Any:
        """
        Récupère une valeur du cache ou l'exécute et la met en cache
        
        Args:
            key: Clé de cache
            callback: Fonction à exécuter si cache miss
            ttl: Durée de vie en secondes
            
        Returns:
            Valeur du cache ou résultat du callback
        """
        value = cache.get(key)
        
        if value is None:
            value = callback()
            cache.set(key, value, timeout=ttl)
            logger.debug(f"Cache MISS: {key}")
        else:
            logger.debug(f"Cache HIT: {key}")
        
        return value
    
    @classmethod
    def invalidate(cls, key: str) -> None:
        """Invalide une clé de cache"""
        cache.delete(key)
        logger.debug(f"Cache INVALIDATED: {key}")
    
    @classmethod
    def invalidate_pattern(cls, pattern: str) -> None:
        """
        Invalide toutes les clés correspondant à un pattern
        
        Args:
            pattern: Pattern de clés (ex: "user:*")
        """
        # Note: Nécessite Redis avec support de SCAN
        from django.core.cache import cache as django_cache
        
        if hasattr(django_cache, 'delete_pattern'):
            django_cache.delete_pattern(pattern)
            logger.debug(f"Cache INVALIDATED (pattern): {pattern}")
    
    @classmethod
    def cache_user(cls, user_id: int, data: dict, ttl: int = TTL_SHORT) -> None:
        """Met en cache les données d'un utilisateur"""
        key = cls._make_key(cls.PREFIX_USER, user_id)
        cache.set(key, data, timeout=ttl)
    
    @classmethod
    def get_cached_user(cls, user_id: int) -> Optional[dict]:
        """Récupère les données d'un utilisateur du cache"""
        key = cls._make_key(cls.PREFIX_USER, user_id)
        return cache.get(key)
    
    @classmethod
    def invalidate_user(cls, user_id: int) -> None:
        """Invalide le cache d'un utilisateur"""
        key = cls._make_key(cls.PREFIX_USER, user_id)
        cls.invalidate(key)
    
    @classmethod
    def cache_agronomist_list(cls, data: List[dict], ttl: int = TTL_MEDIUM) -> None:
        """Met en cache la liste des agronomes"""
        key = cls._make_key(cls.PREFIX_LIST, "agronomists")
        cache.set(key, data, timeout=ttl)
    
    @classmethod
    def get_cached_agronomist_list(cls) -> Optional[List[dict]]:
        """Récupère la liste des agronomes du cache"""
        key = cls._make_key(cls.PREFIX_LIST, "agronomists")
        return cache.get(key)
    
    @classmethod
    def invalidate_agronomist_list(cls) -> None:
        """Invalide le cache de la liste des agronomes"""
        key = cls._make_key(cls.PREFIX_LIST, "agronomists")
        cls.invalidate(key)


def cached_view(ttl: int = CacheManager.TTL_MEDIUM):
    """
    Décorateur pour mettre en cache une vue complète
    
    Usage:
        @cached_view(ttl=3600)
        @api_view(['GET'])
        def my_view(request):
            ...
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        @method_decorator(cache_page(ttl))
        def wrapper(*args, **kwargs):
            return view_func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# PAGINATION CURSOR
# ============================================================================

class StandardCursorPagination(CursorPagination):
    """
    Pagination cursor standard pour grandes listes
    
    Avantages vs PageNumberPagination:
    - Performance constante même pour grandes listes
    - Pas de problème avec les données qui changent
    - Pas de calcul de count() coûteux
    
    Inconvénients:
    - Pas de navigation directe vers une page spécifique
    - Pas de nombre total de pages
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-id'  # Tri par défaut
    
    def get_paginated_response_schema(self, schema):
        """Schéma pour la documentation Swagger"""
        return {
            'type': 'object',
            'properties': {
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'description': 'URL de la page suivante'
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'description': 'URL de la page précédente'
                },
                'results': schema,
            },
        }


class LargeCursorPagination(CursorPagination):
    """Pagination cursor pour très grandes listes (>10k items)"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    ordering = '-id'


class SmallCursorPagination(CursorPagination):
    """Pagination cursor pour petites listes"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    ordering = '-id'


# ============================================================================
# MONITORING DES PERFORMANCES
# ============================================================================

class PerformanceMonitor:
    """
    Moniteur de performances pour identifier les goulots d'étranglement
    """
    
    @staticmethod
    def log_slow_query(func: Callable, threshold: float = 1.0) -> Callable:
        """
        Décorateur pour logger les requêtes lentes
        
        Args:
            func: Fonction à monitorer
            threshold: Seuil en secondes (défaut: 1.0s)
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            if duration > threshold:
                logger.warning(
                    f"SLOW QUERY: {func.__name__} took {duration:.3f}s "
                    f"(threshold: {threshold}s)"
                )
            
            return result
        return wrapper
    
    @staticmethod
    def measure_time(label: str = "Operation"):
        """
        Context manager pour mesurer le temps d'exécution
        
        Usage:
            with PerformanceMonitor.measure_time("My operation"):
                # Code à mesurer
                ...
        """
        class TimeMeasure:
            def __enter__(self):
                self.start = time.time()
                return self
            
            def __exit__(self, *args):
                duration = time.time() - self.start
                logger.info(f"{label}: {duration:.3f}s")
        
        return TimeMeasure()


# ============================================================================
# HELPERS
# ============================================================================

def optimize_queryset_for_serializer(queryset: QuerySet, serializer_class) -> QuerySet:
    """
    Optimise automatiquement un queryset basé sur les champs du serializer
    
    Args:
        queryset: QuerySet à optimiser
        serializer_class: Classe du serializer
        
    Returns:
        QuerySet optimisé
    """
    # Analyser les champs du serializer
    select_related_fields = []
    prefetch_related_fields = []
    
    if hasattr(serializer_class, 'Meta'):
        fields = getattr(serializer_class.Meta, 'fields', [])
        
        # Identifier les relations
        for field_name in fields:
            field = queryset.model._meta.get_field(field_name)
            
            if field.many_to_one or field.one_to_one:
                select_related_fields.append(field_name)
            elif field.many_to_many or field.one_to_many:
                prefetch_related_fields.append(field_name)
    
    # Appliquer les optimisations
    if select_related_fields:
        queryset = queryset.select_related(*select_related_fields)
    
    if prefetch_related_fields:
        queryset = queryset.prefetch_related(*prefetch_related_fields)
    
    return queryset


def clear_all_cache():
    """Vide tout le cache Redis"""
    cache.clear()
    logger.info("All cache cleared")


def get_cache_stats() -> dict:
    """
    Récupère les statistiques du cache
    
    Returns:
        Dict avec les statistiques
    """
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        info = redis_conn.info()
        
        return {
            'used_memory': info.get('used_memory_human'),
            'connected_clients': info.get('connected_clients'),
            'total_commands_processed': info.get('total_commands_processed'),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
            'hit_rate': (
                info.get('keyspace_hits', 0) / 
                (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1))
                * 100
            )
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {}
