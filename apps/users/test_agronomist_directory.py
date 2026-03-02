"""
Tests pour l'annuaire des agronomes
Exigences: 8.1, 8.2, 8.3, 8.4
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient

from apps.locations.models import Region, Prefecture, Canton
from apps.users.models import AgronomeProfile

User = get_user_model()


@pytest.fixture
def api_client():
    """Client API pour les tests"""
    return APIClient()


@pytest.fixture
def setup_locations(db):
    """Crée les données de localisation pour les tests"""
    region = Region.objects.create(nom="Région Maritime", code="MAR")
    prefecture = Prefecture.objects.create(
        nom="Golfe",
        code="GOL",
        region=region
    )
    canton1 = Canton.objects.create(
        nom="Lomé 1er",
        code="LOM1",
        prefecture=prefecture
    )
    canton2 = Canton.objects.create(
        nom="Lomé 2ème",
        code="LOM2",
        prefecture=prefecture
    )
    return {
        'region': region,
        'prefecture': prefecture,
        'canton1': canton1,
        'canton2': canton2
    }


@pytest.fixture
def setup_agronomists(db, setup_locations):
    """Crée des agronomes de test"""
    locations = setup_locations
    
    # Agronome validé dans canton1
    user1 = User.objects.create_user(
        username='agronome1',
        email='agronome1@test.com',
        phone_number='+22890000001',
        password='Test@1234',
        user_type='AGRONOME',
        first_name='Jean',
        last_name='Dupont'
    )
    profile1 = AgronomeProfile.objects.create(
        user=user1,
        canton_rattachement=locations['canton1'],
        specialisations=['Cultures céréalières', 'Irrigation'],
        statut_validation='VALIDE',
        badge_valide=True,
        note_moyenne=4.5,
        nombre_avis=10
    )
    
    # Agronome validé dans canton2
    user2 = User.objects.create_user(
        username='agronome2',
        email='agronome2@test.com',
        phone_number='+22890000002',
        password='Test@1234',
        user_type='AGRONOME',
        first_name='Marie',
        last_name='Martin'
    )
    profile2 = AgronomeProfile.objects.create(
        user=user2,
        canton_rattachement=locations['canton2'],
        specialisations=['Cultures maraîchères', 'Agriculture biologique'],
        statut_validation='VALIDE',
        badge_valide=True,
        note_moyenne=4.8,
        nombre_avis=15
    )
    
    # Agronome en attente de validation (ne doit pas apparaître)
    user3 = User.objects.create_user(
        username='agronome3',
        email='agronome3@test.com',
        phone_number='+22890000003',
        password='Test@1234',
        user_type='AGRONOME',
        first_name='Paul',
        last_name='Bernard'
    )
    profile3 = AgronomeProfile.objects.create(
        user=user3,
        canton_rattachement=locations['canton1'],
        specialisations=['Élevage bovin'],
        statut_validation='EN_ATTENTE',
        badge_valide=False
    )
    
    # Agronome rejeté (ne doit pas apparaître)
    user4 = User.objects.create_user(
        username='agronome4',
        email='agronome4@test.com',
        phone_number='+22890000004',
        password='Test@1234',
        user_type='AGRONOME',
        first_name='Sophie',
        last_name='Dubois'
    )
    profile4 = AgronomeProfile.objects.create(
        user=user4,
        canton_rattachement=locations['canton1'],
        specialisations=['Aviculture'],
        statut_validation='REJETE',
        badge_valide=False
    )
    
    return {
        'profile1': profile1,
        'profile2': profile2,
        'profile3': profile3,
        'profile4': profile4
    }


@pytest.mark.django_db
class TestAgronomeDirectory:
    """Tests pour l'annuaire des agronomes"""
    
    def setup_method(self):
        """Nettoyer le cache avant chaque test"""
        cache.clear()
    
    def test_list_all_validated_agronomists(self, api_client, setup_agronomists):
        """
        Test: Lister tous les agronomes validés
        Exigence: 8.2 - Afficher uniquement les profils validés
        """
        url = reverse('users:agronomist-directory')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2  # Seulement les 2 validés
        assert len(response.data['results']) == 2
        
        # Vérifier que les agronomes sont triés par note moyenne
        assert response.data['results'][0]['note_moyenne'] == '4.80'
        assert response.data['results'][1]['note_moyenne'] == '4.50'
    
    def test_filter_by_canton(self, api_client, setup_agronomists, setup_locations):
        """
        Test: Filtrer par canton
        Exigence: 8.1, 8.3 - Filtrer par canton et afficher tous les agronomes du canton
        """
        url = reverse('users:agronomist-directory')
        canton1_id = setup_locations['canton1'].id
        
        response = api_client.get(url, {'canton': canton1_id})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['canton_nom'] == 'Lomé 1er'
        assert response.data['results'][0]['nom_complet'] == 'Jean Dupont'
    
    def test_filter_by_prefecture(self, api_client, setup_agronomists, setup_locations):
        """
        Test: Filtrer par préfecture
        Exigence: 8.1 - Filtrer par préfecture
        """
        url = reverse('users:agronomist-directory')
        prefecture_id = setup_locations['prefecture'].id
        
        response = api_client.get(url, {'prefecture': prefecture_id})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2  # Les 2 agronomes validés sont dans la même préfecture
    
    def test_filter_by_region(self, api_client, setup_agronomists, setup_locations):
        """
        Test: Filtrer par région
        Exigence: 8.1 - Filtrer par région
        """
        url = reverse('users:agronomist-directory')
        region_id = setup_locations['region'].id
        
        response = api_client.get(url, {'region': region_id})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
    
    def test_filter_by_specialisation(self, api_client, setup_agronomists):
        """
        Test: Filtrer par spécialisation
        Exigence: 8.1 - Filtrer par spécialisation
        """
        url = reverse('users:agronomist-directory')
        
        response = api_client.get(url, {'specialisation': 'Irrigation'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert 'Irrigation' in response.data['results'][0]['specialisations']
    
    def test_agronomist_data_structure(self, api_client, setup_agronomists):
        """
        Test: Structure des données retournées
        Exigence: 8.4 - Afficher nom, spécialisations, Canton, note moyenne, nombre d'avis
        """
        url = reverse('users:agronomist-directory')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        agronomist = response.data['results'][0]
        
        # Vérifier que tous les champs requis sont présents
        assert 'id' in agronomist
        assert 'nom_complet' in agronomist
        assert 'specialisations' in agronomist
        assert 'canton_nom' in agronomist
        assert 'prefecture_nom' in agronomist
        assert 'region_nom' in agronomist
        assert 'note_moyenne' in agronomist
        assert 'nombre_avis' in agronomist
        assert 'badge_valide' in agronomist
        
        # Vérifier les valeurs
        assert agronomist['badge_valide'] is True
        assert isinstance(agronomist['specialisations'], list)
        assert len(agronomist['specialisations']) > 0
    
    def test_pagination(self, api_client, setup_agronomists):
        """
        Test: Pagination de l'annuaire
        """
        url = reverse('users:agronomist-directory')
        
        # Page 1 avec 1 élément par page
        response = api_client.get(url, {'page': 1, 'page_size': 1})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert response.data['num_pages'] == 2
        assert response.data['current_page'] == 1
        assert response.data['page_size'] == 1
        assert len(response.data['results']) == 1
        assert response.data['next'] is True
        assert response.data['previous'] is False
    
    def test_pagination_page_2(self, api_client, setup_agronomists):
        """
        Test: Pagination - page 2
        """
        url = reverse('users:agronomist-directory')
        
        response = api_client.get(url, {'page': 2, 'page_size': 1})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['current_page'] == 2
        assert len(response.data['results']) == 1
        assert response.data['next'] is False
        assert response.data['previous'] is True
    
    def test_max_page_size(self, api_client, setup_agronomists):
        """
        Test: Limite maximale de page_size
        """
        url = reverse('users:agronomist-directory')
        
        # Demander 200 éléments, mais max est 100
        response = api_client.get(url, {'page_size': 200})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['page_size'] == 100
    
    def test_invalid_pagination_params(self, api_client, setup_agronomists):
        """
        Test: Paramètres de pagination invalides
        """
        url = reverse('users:agronomist-directory')
        
        response = api_client.get(url, {'page': 'invalid'})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_cache_is_used(self, api_client, setup_agronomists):
        """
        Test: Le cache Redis est utilisé
        Exigence: Optimiser avec cache Redis
        """
        url = reverse('users:agronomist-directory')
        
        # Première requête - pas de cache
        response1 = api_client.get(url)
        assert response1.status_code == status.HTTP_200_OK
        
        # Modifier un agronome dans la base
        profile = setup_agronomists['profile1']
        profile.note_moyenne = 5.0
        profile.save()
        
        # Deuxième requête - devrait utiliser le cache (note non mise à jour)
        response2 = api_client.get(url)
        assert response2.status_code == status.HTTP_200_OK
        
        # Les données devraient être identiques (cache)
        assert response1.data == response2.data
        
        # Vider le cache
        cache.clear()
        
        # Troisième requête - devrait récupérer les nouvelles données
        response3 = api_client.get(url)
        assert response3.status_code == status.HTTP_200_OK
        
        # Maintenant la note devrait être mise à jour
        # (Trouver l'agronome avec la meilleure note)
        best_agronomist = max(response3.data['results'], key=lambda x: float(x['note_moyenne']))
        assert float(best_agronomist['note_moyenne']) == 5.0
    
    def test_no_validated_agronomists(self, api_client, setup_locations):
        """
        Test: Aucun agronome validé
        """
        url = reverse('users:agronomist-directory')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert len(response.data['results']) == 0
    
    def test_combined_filters(self, api_client, setup_agronomists, setup_locations):
        """
        Test: Combinaison de filtres
        """
        url = reverse('users:agronomist-directory')
        canton1_id = setup_locations['canton1'].id
        
        response = api_client.get(url, {
            'canton': canton1_id,
            'specialisation': 'Irrigation'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['canton_nom'] == 'Lomé 1er'
        assert 'Irrigation' in response.data['results'][0]['specialisations']
    
    def test_public_access(self, api_client, setup_agronomists):
        """
        Test: L'annuaire est accessible sans authentification
        """
        url = reverse('users:agronomist-directory')
        
        # Pas d'authentification
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
