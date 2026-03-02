"""
Tests pour l'endpoint des fonctionnalités premium
Exigences: 10.5
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import ExploitantProfile
from apps.locations.models import Region, Prefecture, Canton

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def region():
    return Region.objects.create(nom="Région Maritime", code="MAR")


@pytest.fixture
def prefecture(region):
    return Prefecture.objects.create(
        nom="Golfe",
        code="GOL",
        region=region
    )


@pytest.fixture
def canton(prefecture):
    return Canton.objects.create(
        nom="Lomé 1er",
        code="LOM1",
        prefecture=prefecture
    )


@pytest.fixture
def exploitant_non_verifie(canton):
    """Exploitant avec profil non vérifié"""
    user = User.objects.create_user(
        username='exploitant_test',
        email='exploitant@test.com',
        phone_number='+22890000001',
        password='Test@1234',
        user_type='EXPLOITANT'
    )
    user.phone_verified = True
    user.save()
    
    profile = ExploitantProfile.objects.create(
        user=user,
        superficie_totale=15.5,
        canton_principal=canton,
        coordonnees_gps={'lat': 6.1, 'lon': 1.2},
        statut_verification='NON_VERIFIE'
    )
    
    return user


@pytest.fixture
def exploitant_verifie(canton):
    """Exploitant avec profil vérifié"""
    user = User.objects.create_user(
        username='exploitant_verifie',
        email='verifie@test.com',
        phone_number='+22890000002',
        password='Test@1234',
        user_type='EXPLOITANT'
    )
    user.phone_verified = True
    user.save()
    
    profile = ExploitantProfile.objects.create(
        user=user,
        superficie_totale=20.0,
        canton_principal=canton,
        coordonnees_gps={'lat': 6.1, 'lon': 1.2},
        statut_verification='VERIFIE'
    )
    
    return user


@pytest.fixture
def exploitant_en_attente(canton):
    """Exploitant avec demande en attente"""
    user = User.objects.create_user(
        username='exploitant_attente',
        email='attente@test.com',
        phone_number='+22890000003',
        password='Test@1234',
        user_type='EXPLOITANT'
    )
    user.phone_verified = True
    user.save()
    
    profile = ExploitantProfile.objects.create(
        user=user,
        superficie_totale=12.0,
        canton_principal=canton,
        coordonnees_gps={'lat': 6.1, 'lon': 1.2},
        statut_verification='EN_ATTENTE'
    )
    
    return user


@pytest.fixture
def exploitant_rejete(canton):
    """Exploitant avec demande rejetée"""
    user = User.objects.create_user(
        username='exploitant_rejete',
        email='rejete@test.com',
        phone_number='+22890000004',
        password='Test@1234',
        user_type='EXPLOITANT'
    )
    user.phone_verified = True
    user.save()
    
    profile = ExploitantProfile.objects.create(
        user=user,
        superficie_totale=8.0,
        canton_principal=canton,
        coordonnees_gps={'lat': 6.1, 'lon': 1.2},
        statut_verification='REJETE',
        motif_rejet='Superficie insuffisante'
    )
    
    return user


@pytest.fixture
def non_exploitant():
    """Utilisateur qui n'est pas un exploitant"""
    user = User.objects.create_user(
        username='acheteur_test',
        email='acheteur@test.com',
        phone_number='+22890000005',
        password='Test@1234',
        user_type='ACHETEUR'
    )
    user.phone_verified = True
    user.save()
    
    return user


@pytest.mark.django_db
class TestPremiumFeaturesEndpoint:
    """Tests pour GET /api/v1/farms/me/premium-features"""
    
    def test_exploitant_verifie_acces_complet(self, api_client, exploitant_verifie):
        """
        Test: Un exploitant vérifié a accès à toutes les fonctionnalités premium
        Exigence: 10.5
        """
        api_client.force_authenticate(user=exploitant_verifie)
        
        response = api_client.get('/api/v1/farms/me/premium-features')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Vérifier le statut
        assert data['is_verified'] is True
        assert data['statut_verification'] == 'VERIFIE'
        
        # Vérifier que toutes les fonctionnalités sont activées
        features = data['features']
        assert features['dashboard_avance']['enabled'] is True
        assert features['recrutement_agronomes']['enabled'] is True
        assert features['recrutement_ouvriers']['enabled'] is True
        assert features['prevente_agricole']['enabled'] is True
        assert features['analyses_marche']['enabled'] is True
        assert features['optimisation_logistique']['enabled'] is True
        assert features['recommandations_cultures']['enabled'] is True
        assert features['irrigation_intelligente']['enabled'] is True
        
        # Vérifier les descriptions
        assert 'description' in features['dashboard_avance']
        assert 'description' in features['recrutement_agronomes']
    
    def test_exploitant_non_verifie_acces_refuse(self, api_client, exploitant_non_verifie):
        """
        Test: Un exploitant non vérifié n'a pas accès aux fonctionnalités premium
        Exigence: 10.5
        """
        api_client.force_authenticate(user=exploitant_non_verifie)
        
        response = api_client.get('/api/v1/farms/me/premium-features')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Vérifier le statut
        assert data['is_verified'] is False
        assert data['statut_verification'] == 'NON_VERIFIE'
        
        # Vérifier que toutes les fonctionnalités sont désactivées
        features = data['features']
        assert features['dashboard_avance']['enabled'] is False
        assert features['recrutement_agronomes']['enabled'] is False
        assert features['recrutement_ouvriers']['enabled'] is False
        assert features['prevente_agricole']['enabled'] is False
        assert features['analyses_marche']['enabled'] is False
        assert features['optimisation_logistique']['enabled'] is False
        assert features['recommandations_cultures']['enabled'] is False
        assert features['irrigation_intelligente']['enabled'] is False
        
        # Vérifier le message
        assert 'message' in data
        assert 'vérifiée' in data['message'].lower()
    
    def test_exploitant_en_attente_message_specifique(self, api_client, exploitant_en_attente):
        """
        Test: Un exploitant en attente reçoit un message spécifique
        Exigence: 10.5
        """
        api_client.force_authenticate(user=exploitant_en_attente)
        
        response = api_client.get('/api/v1/farms/me/premium-features')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data['is_verified'] is False
        assert data['statut_verification'] == 'EN_ATTENTE'
        assert 'en cours de traitement' in data['message'].lower()
    
    def test_exploitant_rejete_message_avec_motif(self, api_client, exploitant_rejete):
        """
        Test: Un exploitant rejeté reçoit le motif du rejet
        Exigence: 10.6
        """
        api_client.force_authenticate(user=exploitant_rejete)
        
        response = api_client.get('/api/v1/farms/me/premium-features')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data['is_verified'] is False
        assert data['statut_verification'] == 'REJETE'
        assert 'rejetée' in data['message'].lower()
        assert 'Superficie insuffisante' in data['message']
    
    def test_non_exploitant_acces_refuse(self, api_client, non_exploitant):
        """
        Test: Un utilisateur qui n'est pas exploitant ne peut pas accéder à l'endpoint
        Exigence: 10.5
        """
        api_client.force_authenticate(user=non_exploitant)
        
        response = api_client.get('/api/v1/farms/me/premium-features')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        
        assert 'error' in data
        assert 'code' in data
        assert data['code'] == 'NOT_EXPLOITANT'
        assert 'exploitants' in data['error'].lower()
    
    def test_utilisateur_non_authentifie(self, api_client):
        """
        Test: Un utilisateur non authentifié ne peut pas accéder à l'endpoint
        """
        response = api_client.get('/api/v1/farms/me/premium-features')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_exploitant_sans_profil(self, api_client):
        """
        Test: Un exploitant sans profil reçoit une erreur appropriée
        """
        user = User.objects.create_user(
            username='exploitant_sans_profil',
            email='sans_profil@test.com',
            phone_number='+22890000006',
            password='Test@1234',
            user_type='EXPLOITANT'
        )
        user.phone_verified = True
        user.save()
        
        api_client.force_authenticate(user=user)
        
        response = api_client.get('/api/v1/farms/me/premium-features')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        
        assert 'error' in data
        assert 'code' in data
        assert data['code'] == 'PROFILE_NOT_FOUND'
        assert data['is_verified'] is False
        assert 'message' in data
        assert 'vérification' in data['message'].lower()
    
    def test_structure_reponse_complete(self, api_client, exploitant_verifie):
        """
        Test: La structure de la réponse contient tous les champs requis
        Exigence: 10.5
        """
        api_client.force_authenticate(user=exploitant_verifie)
        
        response = api_client.get('/api/v1/farms/me/premium-features')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Vérifier la structure de base
        assert 'is_verified' in data
        assert 'statut_verification' in data
        assert 'features' in data
        
        # Vérifier que chaque fonctionnalité a la structure attendue
        expected_features = [
            'dashboard_avance',
            'recrutement_agronomes',
            'recrutement_ouvriers',
            'prevente_agricole',
            'analyses_marche',
            'optimisation_logistique',
            'recommandations_cultures',
            'irrigation_intelligente'
        ]
        
        for feature_name in expected_features:
            assert feature_name in data['features']
            feature = data['features'][feature_name]
            assert 'enabled' in feature
            assert 'description' in feature
            assert isinstance(feature['enabled'], bool)
            assert isinstance(feature['description'], str)
            assert len(feature['description']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
