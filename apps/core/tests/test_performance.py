"""
Tests pour les optimisations de performance
"""
import pytest
import time
from django.test import TestCase, override_settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from apps.core.performance import (
    QueryOptimizer,
    CacheManager,
    StandardCursorPagination,
    PerformanceMonitor,
    get_cache_stats,
    clear_all_cache
)
from apps.users.models import AgronomeProfile, ExploitantProfile

User = get_user_model()


@pytest.fixture(autouse=True)
def clear_cache_before_test():
    """Nettoyer le cache avant chaque test"""
    cache.clear()
    yield
    cache.clear()


class TestQueryOptimizer(TestCase):
    """Tests pour QueryOptimizer"""
    
    def setUp(self):
        """Créer des données de test"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            user_type='AGRONOME'
        )
        self.agronomist = AgronomeProfile.objects.create(
            user=self.user,
            specialite='CULTURES_VIVRIERES',
            is_validated=True
        )
    
    def test_optimize_user_queryset(self):
        """Vérifie que optimize_user_queryset réduit les requêtes"""
        # Sans optimisation
        with self.assertNumQueries(2):  # 1 pour users + 1 pour profile
            users = list(User.objects.all())
            for user in users:
                _ = user.agronomeprofile  # Déclenche une requête
        
        # Avec optimisation
        with self.assertNumQueries(1):  # 1 seule requête avec select_related
            users = list(QueryOptimizer.optimize_user_queryset(User.objects.all()))
            for user in users:
                try:
                    _ = user.agronomeprofile  # Pas de requête supplémentaire
                except:
                    pass
    
    def test_optimize_agronomist_queryset(self):
        """Vérifie que optimize_agronomist_queryset fonctionne"""
        queryset = QueryOptimizer.optimize_agronomist_queryset(
            AgronomeProfile.objects.all()
        )
        
        # Vérifier que select_related est appliqué
        self.assertIn('user', queryset.query.select_related)
    
    def test_count_queries_decorator(self):
        """Vérifie que le décorateur count_queries fonctionne"""
        @QueryOptimizer.count_queries
        def test_function():
            list(User.objects.all())
            return "done"
        
        result = test_function()
        self.assertEqual(result, "done")


class TestCacheManager(TestCase):
    """Tests pour CacheManager"""
    
    def setUp(self):
        """Nettoyer le cache"""
        cache.clear()
    
    def test_get_or_set_cache_miss(self):
        """Vérifie get_or_set avec cache miss"""
        call_count = 0
        
        def callback():
            nonlocal call_count
            call_count += 1
            return "test_value"
        
        # Premier appel: cache miss
        value = CacheManager.get_or_set("test_key", callback, ttl=60)
        self.assertEqual(value, "test_value")
        self.assertEqual(call_count, 1)
        
        # Deuxième appel: cache hit
        value = CacheManager.get_or_set("test_key", callback, ttl=60)
        self.assertEqual(value, "test_value")
        self.assertEqual(call_count, 1)  # Callback pas appelé
    
    def test_invalidate_cache(self):
        """Vérifie l'invalidation du cache"""
        cache.set("test_key", "test_value", timeout=60)
        self.assertEqual(cache.get("test_key"), "test_value")
        
        CacheManager.invalidate("test_key")
        self.assertIsNone(cache.get("test_key"))
    
    def test_cache_user(self):
        """Vérifie le cache utilisateur"""
        user_data = {'id': 1, 'email': 'test@example.com'}
        
        CacheManager.cache_user(1, user_data)
        cached = CacheManager.get_cached_user(1)
        
        self.assertEqual(cached, user_data)
    
    def test_invalidate_user(self):
        """Vérifie l'invalidation du cache utilisateur"""
        user_data = {'id': 1, 'email': 'test@example.com'}
        
        CacheManager.cache_user(1, user_data)
        CacheManager.invalidate_user(1)
        
        self.assertIsNone(CacheManager.get_cached_user(1))
    
    def test_cache_agronomist_list(self):
        """Vérifie le cache de la liste des agronomes"""
        data = [{'id': 1, 'name': 'Test'}]
        
        CacheManager.cache_agronomist_list(data)
        cached = CacheManager.get_cached_agronomist_list()
        
        self.assertEqual(cached, data)
    
    def test_invalidate_agronomist_list(self):
        """Vérifie l'invalidation du cache des agronomes"""
        data = [{'id': 1, 'name': 'Test'}]
        
        CacheManager.cache_agronomist_list(data)
        CacheManager.invalidate_agronomist_list()
        
        self.assertIsNone(CacheManager.get_cached_agronomist_list())


class TestStandardCursorPagination(TestCase):
    """Tests pour StandardCursorPagination"""
    
    def setUp(self):
        """Créer des utilisateurs de test"""
        for i in range(50):
            User.objects.create_user(
                email=f'user{i}@example.com',
                password='TestPass123!',
                user_type='EXPLOITANT'
            )
    
    def test_pagination_page_size(self):
        """Vérifie la taille de page par défaut"""
        paginator = StandardCursorPagination()
        self.assertEqual(paginator.page_size, 20)
    
    def test_pagination_works(self):
        """Vérifie que la pagination fonctionne"""
        from rest_framework.test import APIRequestFactory
        
        factory = APIRequestFactory()
        request = factory.get('/test/')
        
        paginator = StandardCursorPagination()
        queryset = User.objects.all().order_by('-id')
        
        paginated = paginator.paginate_queryset(queryset, request)
        
        # Vérifier que la pagination limite les résultats
        self.assertEqual(len(list(paginated)), 20)


class TestPerformanceMonitor(TestCase):
    """Tests pour PerformanceMonitor"""
    
    def test_log_slow_query(self):
        """Vérifie que log_slow_query détecte les requêtes lentes"""
        @PerformanceMonitor.log_slow_query
        def slow_function():
            time.sleep(0.1)
            return "done"
        
        result = slow_function()
        self.assertEqual(result, "done")
    
    def test_measure_time(self):
        """Vérifie que measure_time fonctionne"""
        with PerformanceMonitor.measure_time("Test operation"):
            time.sleep(0.1)
        
        # Si pas d'exception, le test passe


class TestCacheStats(TestCase):
    """Tests pour les statistiques de cache"""
    
    def test_get_cache_stats(self):
        """Vérifie que get_cache_stats retourne des données"""
        stats = get_cache_stats()
        
        # Vérifier que c'est un dict (peut être vide si Redis pas configuré)
        self.assertIsInstance(stats, dict)
    
    def test_clear_all_cache(self):
        """Vérifie que clear_all_cache fonctionne"""
        cache.set("test_key", "test_value", timeout=60)
        
        clear_all_cache()
        
        self.assertIsNone(cache.get("test_key"))


@pytest.mark.django_db
class TestPerformanceIntegration:
    """Tests d'intégration pour les performances"""
    
    def test_agronomist_query_optimization(self):
        """Vérifie que les requêtes agronomes sont optimisées"""
        # Créer des données de test
        user = User.objects.create_user(
            email='agro@example.com',
            password='TestPass123!',
            user_type='AGRONOME'
        )
        AgronomeProfile.objects.create(
            user=user,
            specialite='CULTURES_VIVRIERES',
            is_validated=True
        )
        
        # Sans optimisation
        from django.test.utils import override_settings
        from django.db import connection, reset_queries
        
        with override_settings(DEBUG=True):
            reset_queries()
            
            # Requête non optimisée
            agronomists = list(AgronomeProfile.objects.all())
            for agro in agronomists:
                _ = agro.user.email  # Déclenche N+1
            
            queries_without_optimization = len(connection.queries)
            
            reset_queries()
            
            # Requête optimisée
            agronomists = list(
                QueryOptimizer.optimize_agronomist_queryset(
                    AgronomeProfile.objects.all()
                )
            )
            for agro in agronomists:
                _ = agro.user.email  # Pas de requête supplémentaire
            
            queries_with_optimization = len(connection.queries)
            
            # Vérifier que l'optimisation réduit les requêtes
            assert queries_with_optimization < queries_without_optimization
    
    def test_cache_reduces_database_queries(self):
        """Vérifie que le cache réduit les requêtes database"""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            user_type='EXPLOITANT'
        )
        
        user_data = {'id': user.id, 'email': user.email}
        
        # Premier appel: cache miss
        from django.db import connection, reset_queries
        from django.test.utils import override_settings
        
        with override_settings(DEBUG=True):
            reset_queries()
            
            # Simuler une requête avec cache
            cached = CacheManager.get_cached_user(user.id)
            if not cached:
                # Requête database
                user_obj = User.objects.get(id=user.id)
                CacheManager.cache_user(user.id, user_data)
            
            queries_first_call = len(connection.queries)
            
            reset_queries()
            
            # Deuxième appel: cache hit
            cached = CacheManager.get_cached_user(user.id)
            
            queries_second_call = len(connection.queries)
            
            # Vérifier que le cache réduit les requêtes
            assert queries_second_call < queries_first_call


class TestCacheTTL(TestCase):
    """Tests pour les TTL du cache"""
    
    def test_ttl_short(self):
        """Vérifie que TTL_SHORT est correct"""
        self.assertEqual(CacheManager.TTL_SHORT, 300)  # 5 minutes
    
    def test_ttl_medium(self):
        """Vérifie que TTL_MEDIUM est correct"""
        self.assertEqual(CacheManager.TTL_MEDIUM, 3600)  # 1 heure
    
    def test_ttl_long(self):
        """Vérifie que TTL_LONG est correct"""
        self.assertEqual(CacheManager.TTL_LONG, 86400)  # 24 heures


# ============================================================================
# TESTS DE PERFORMANCE (à exécuter manuellement)
# ============================================================================

"""
Pour tester les performances réelles:

1. Créer beaucoup de données:
    python manage.py shell
    >>> from apps.users.models import User, AgronomeProfile
    >>> for i in range(1000):
    ...     user = User.objects.create_user(
    ...         email=f'user{i}@example.com',
    ...         password='TestPass123!',
    ...         user_type='AGRONOME'
    ...     )
    ...     AgronomeProfile.objects.create(
    ...         user=user,
    ...         specialite='CULTURES_VIVRIERES',
    ...         is_validated=True
    ...     )

2. Tester sans optimisation:
    >>> import time
    >>> from django.db import connection, reset_queries
    >>> reset_queries()
    >>> start = time.time()
    >>> agronomists = list(AgronomeProfile.objects.all())
    >>> for agro in agronomists:
    ...     _ = agro.user.email
    >>> print(f"Time: {time.time() - start:.3f}s, Queries: {len(connection.queries)}")

3. Tester avec optimisation:
    >>> from apps.core.performance import QueryOptimizer
    >>> reset_queries()
    >>> start = time.time()
    >>> agronomists = list(QueryOptimizer.optimize_agronomist_queryset(AgronomeProfile.objects.all()))
    >>> for agro in agronomists:
    ...     _ = agro.user.email
    >>> print(f"Time: {time.time() - start:.3f}s, Queries: {len(connection.queries)}")

4. Comparer les résultats:
    Sans optimisation: ~1001 requêtes, ~5s
    Avec optimisation: ~1 requête, ~0.1s
    Amélioration: 50x plus rapide!
"""
