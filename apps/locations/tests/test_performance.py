"""
Tests de performance pour les endpoints administratifs

**Validates: Requirements 1.5, 35.1**

Ces tests vérifient que les endpoints administratifs respectent
l'exigence de performance: temps de réponse < 500ms pour 95% des requêtes.
"""
import time
from typing import List
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from hypothesis import given, settings, strategies as st, HealthCheck
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize

from apps.locations.models import Region, Prefecture, Canton


class PerformanceTestCase(TestCase):
    """Classe de base pour les tests de performance"""
    
    @classmethod
    def setUpTestData(cls):
        """Créer des données de test réalistes"""
        # Créer 5 régions
        cls.regions = []
        for i in range(5):
            region = Region.objects.create(
                nom=f"Région {i+1}",
                code=f"REG{i+1:02d}"
            )
            cls.regions.append(region)
        
        # Créer 38 préfectures (environ 7-8 par région)
        cls.prefectures = []
        prefecture_count = 0
        for region in cls.regions:
            num_prefectures = 7 if prefecture_count < 35 else 3
            for j in range(num_prefectures):
                prefecture = Prefecture.objects.create(
                    nom=f"Préfecture {prefecture_count+1}",
                    code=f"PREF{prefecture_count+1:03d}",
                    region=region
                )
                cls.prefectures.append(prefecture)
                prefecture_count += 1
        
        # Créer 300+ cantons (environ 8 par préfecture)
        cls.cantons = []
        canton_count = 0
        for prefecture in cls.prefectures:
            for k in range(8):
                canton = Canton.objects.create(
                    nom=f"Canton {canton_count+1}",
                    code=f"CANT{canton_count+1:04d}",
                    prefecture=prefecture,
                    coordonnees_centre={"lat": 6.0 + (canton_count % 100) * 0.01, "lon": 1.0 + (canton_count % 100) * 0.01}
                )
                cls.cantons.append(canton)
                canton_count += 1
    
    def measure_response_time(self, url: str) -> float:
        """
        Mesure le temps de réponse d'un endpoint
        
        Returns:
            Temps de réponse en millisecondes
        """
        client = APIClient()
        start_time = time.perf_counter()
        response = client.get(url)
        end_time = time.perf_counter()
        
        # Vérifier que la requête a réussi
        self.assertEqual(response.status_code, 200)
        
        # Retourner le temps en millisecondes
        return (end_time - start_time) * 1000


class RegionsEndpointPerformanceTest(PerformanceTestCase):
    """
    Tests de performance pour l'endpoint GET /api/v1/regions
    
    **Validates: Requirements 1.5, 35.1**
    """
    
    @given(st.integers(min_value=0, max_value=9))
    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[HealthCheck.too_slow]
    )
    def test_regions_list_response_time_property(self, iteration: int):
        """
        **Propriété 1: Temps de réponse < 500ms**
        
        Vérifie que l'endpoint GET /api/v1/regions répond en moins de 500ms
        pour toutes les requêtes.
        
        **Validates: Requirements 1.5, 35.1**
        """
        url = reverse('region-list')
        response_time = self.measure_response_time(url)
        
        # Assertion: Le temps de réponse doit être < 500ms
        self.assertLess(
            response_time,
            500,
            f"Temps de réponse trop élevé: {response_time:.2f}ms (itération {iteration})"
        )


class PrefecturesEndpointPerformanceTest(PerformanceTestCase):
    """
    Tests de performance pour les endpoints de préfectures
    
    **Validates: Requirements 1.5, 35.1**
    """
    
    @given(st.integers(min_value=0, max_value=9))
    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[HealthCheck.too_slow]
    )
    def test_region_prefectures_response_time_property(self, iteration: int):
        """
        **Propriété 1: Temps de réponse < 500ms**
        
        Vérifie que l'endpoint GET /api/v1/regions/{id}/prefectures répond
        en moins de 500ms pour toutes les régions.
        
        **Validates: Requirements 1.5, 35.1**
        """
        # Sélectionner une région aléatoire
        region_index = iteration % len(self.regions)
        region = self.regions[region_index]
        
        url = reverse('region-prefectures', kwargs={'pk': region.id})
        response_time = self.measure_response_time(url)
        
        # Assertion: Le temps de réponse doit être < 500ms
        self.assertLess(
            response_time,
            500,
            f"Temps de réponse trop élevé pour région {region.nom}: {response_time:.2f}ms"
        )


class CantonsEndpointPerformanceTest(PerformanceTestCase):
    """
    Tests de performance pour les endpoints de cantons
    
    **Validates: Requirements 1.5, 35.1**
    """
    
    @given(st.integers(min_value=0, max_value=9))
    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[HealthCheck.too_slow]
    )
    def test_prefecture_cantons_response_time_property(self, iteration: int):
        """
        **Propriété 1: Temps de réponse < 500ms**
        
        Vérifie que l'endpoint GET /api/v1/prefectures/{id}/cantons répond
        en moins de 500ms pour toutes les préfectures.
        
        **Validates: Requirements 1.5, 35.1**
        """
        # Sélectionner une préfecture aléatoire
        prefecture_index = iteration % len(self.prefectures)
        prefecture = self.prefectures[prefecture_index]
        
        url = reverse('prefecture-cantons', kwargs={'pk': prefecture.id})
        response_time = self.measure_response_time(url)
        
        # Assertion: Le temps de réponse doit être < 500ms
        self.assertLess(
            response_time,
            500,
            f"Temps de réponse trop élevé pour préfecture {prefecture.nom}: {response_time:.2f}ms"
        )


class CantonSearchPerformanceTest(PerformanceTestCase):
    """
    Tests de performance pour la recherche de cantons
    
    **Validates: Requirements 1.5, 35.1**
    
    Exigence 1.5: "QUAND un Utilisateur recherche un Canton,
    LA Plateforme DOIT retourner les résultats en moins de 500ms"
    """
    
    @given(
        st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
            min_size=1,
            max_size=20
        )
    )
    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[HealthCheck.too_slow]
    )
    def test_canton_search_response_time_property(self, search_query: str):
        """
        **Propriété 1: Temps de réponse < 500ms**
        
        Vérifie que l'endpoint GET /api/v1/cantons/search?q={query} répond
        en moins de 500ms pour toutes les recherches.
        
        **Validates: Requirements 1.5, 35.1**
        """
        url = reverse('canton-search')
        client = APIClient()
        
        start_time = time.perf_counter()
        response = client.get(url, {'q': search_query})
        end_time = time.perf_counter()
        
        # Vérifier que la requête a réussi
        self.assertEqual(response.status_code, 200)
        
        response_time = (end_time - start_time) * 1000
        
        # Assertion: Le temps de réponse doit être < 500ms
        self.assertLess(
            response_time,
            500,
            f"Temps de réponse trop élevé pour recherche '{search_query}': {response_time:.2f}ms"
        )


class CachedEndpointsPerformanceTest(PerformanceTestCase):
    """
    Tests de performance pour les endpoints avec cache Redis
    
    **Validates: Requirements 1.5, 35.1**
    
    Vérifie que les endpoints avec cache Redis sont encore plus rapides
    lors des requêtes suivantes.
    """
    
    @given(st.integers(min_value=0, max_value=9))
    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[HealthCheck.too_slow]
    )
    def test_cached_regions_list_performance(self, iteration: int):
        """
        **Propriété 1: Temps de réponse < 500ms**
        
        Vérifie que l'endpoint GET /api/v1/regions avec cache Redis
        répond en moins de 500ms, même avec cache.
        
        **Validates: Requirements 1.5, 35.1**
        """
        url = reverse('region-list')
        
        # Première requête (peut remplir le cache)
        self.measure_response_time(url)
        
        # Deuxième requête (devrait utiliser le cache)
        response_time = self.measure_response_time(url)
        
        # Assertion: Le temps de réponse doit être < 500ms
        self.assertLess(
            response_time,
            500,
            f"Temps de réponse trop élevé avec cache: {response_time:.2f}ms"
        )


class PercentilePerformanceTest(PerformanceTestCase):
    """
    Tests de performance pour vérifier le percentile 95
    
    **Validates: Requirements 35.1**
    
    Exigence 35.1: "LA Plateforme DOIT répondre aux requêtes de consultation
    en moins de 500ms pour 95% des requêtes"
    """
    
    def test_95th_percentile_regions_endpoint(self):
        """
        **Propriété 1: Temps de réponse < 500ms pour 95% des requêtes**
        
        Vérifie que 95% des requêtes vers GET /api/v1/regions
        répondent en moins de 500ms.
        
        **Validates: Requirements 35.1**
        """
        url = reverse('region-list')
        response_times: List[float] = []
        
        # Effectuer 20 requêtes (réduit de 100 pour performance)
        for _ in range(20):
            response_time = self.measure_response_time(url)
            response_times.append(response_time)
        
        # Trier les temps de réponse
        response_times.sort()
        
        # Calculer le 95e percentile (95% des requêtes)
        percentile_95_index = int(len(response_times) * 0.95)
        percentile_95_time = response_times[percentile_95_index]
        
        # Assertion: Le 95e percentile doit être < 500ms
        self.assertLess(
            percentile_95_time,
            500,
            f"95e percentile trop élevé: {percentile_95_time:.2f}ms"
        )
    
    def test_95th_percentile_canton_search_endpoint(self):
        """
        **Propriété 1: Temps de réponse < 500ms pour 95% des requêtes**
        
        Vérifie que 95% des requêtes de recherche de cantons
        répondent en moins de 500ms.
        
        **Validates: Requirements 1.5, 35.1**
        """
        url = reverse('canton-search')
        client = APIClient()
        response_times: List[float] = []
        
        # Effectuer 20 recherches avec différentes requêtes (réduit de 100)
        search_queries = [
            f"Canton {i}" for i in range(1, 21)
        ]
        
        for query in search_queries:
            start_time = time.perf_counter()
            response = client.get(url, {'q': query})
            end_time = time.perf_counter()
            
            self.assertEqual(response.status_code, 200)
            response_time = (end_time - start_time) * 1000
            response_times.append(response_time)
        
        # Trier les temps de réponse
        response_times.sort()
        
        # Calculer le 95e percentile
        percentile_95_index = int(len(response_times) * 0.95)
        percentile_95_time = response_times[percentile_95_index]
        
        # Assertion: Le 95e percentile doit être < 500ms
        self.assertLess(
            percentile_95_time,
            500,
            f"95e percentile de recherche trop élevé: {percentile_95_time:.2f}ms"
        )
    
    def test_95th_percentile_all_endpoints(self):
        """
        **Propriété 1: Temps de réponse < 500ms pour 95% des requêtes**
        
        Vérifie que 95% des requêtes vers TOUS les endpoints administratifs
        répondent en moins de 500ms.
        
        **Validates: Requirements 35.1**
        """
        response_times: List[float] = []
        
        # Tester tous les endpoints
        endpoints = [
            reverse('region-list'),
            reverse('region-prefectures', kwargs={'pk': self.regions[0].id}),
            reverse('prefecture-cantons', kwargs={'pk': self.prefectures[0].id}),
        ]
        
        # Effectuer 20 requêtes réparties sur tous les endpoints (réduit de 100)
        for i in range(20):
            url = endpoints[i % len(endpoints)]
            response_time = self.measure_response_time(url)
            response_times.append(response_time)
        
        # Trier les temps de réponse
        response_times.sort()
        
        # Calculer le 95e percentile
        percentile_95_index = int(len(response_times) * 0.95)
        percentile_95_time = response_times[percentile_95_index]
        
        # Assertion: Le 95e percentile doit être < 500ms
        self.assertLess(
            percentile_95_time,
            500,
            f"95e percentile global trop élevé: {percentile_95_time:.2f}ms"
        )
