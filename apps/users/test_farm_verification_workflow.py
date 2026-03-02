"""
Tests pour le workflow de validation des exploitations agricoles
Exigences: 10.4, 10.5, 10.6
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import ExploitantProfile
from apps.users.services import FarmVerificationService
from apps.locations.models import Region, Prefecture, Canton

User = get_user_model()


@pytest.mark.django_db
class TestFarmVerificationWorkflow(TestCase):
    """
    Tests pour le workflow de validation des exploitations
    """
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = APIClient()
        
        # Créer les données géographiques
        self.region = Region.objects.create(nom='Maritime', code='MAR')
        self.prefecture = Prefecture.objects.create(
            nom='Golfe',
            code='GOL',
            region=self.region
        )
        self.canton = Canton.objects.create(
            nom='Lomé 1er',
            code='LOM1',
            prefecture=self.prefecture
        )
        
        # Créer un administrateur
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            phone_number='+22890000001',
            password='Admin@123',
            user_type='ADMIN',
            is_staff=True,
            is_superuser=True
        )
        
        # Créer un exploitant avec profil en attente
        self.exploitant = User.objects.create_user(
            username='exploitant1',
            email='exploitant1@test.com',
            phone_number='+22890000002',
            password='Test@123',
            user_type='EXPLOITANT',
            first_name='Jean',
            last_name='Dupont'
        )
        
        self.exploitant_profile = ExploitantProfile.objects.create(
            user=self.exploitant,
            superficie_totale=15.5,
            canton_principal=self.canton,
            coordonnees_gps={'lat': 6.1319, 'lon': 1.2228},
            cultures_actuelles=['Maïs', 'Manioc'],
            statut_verification='EN_ATTENTE'
        )
    
    def test_verify_farm_success(self):
        """
        Test: Validation réussie d'une exploitation
        Exigence: 10.5
        """
        # Se connecter en tant qu'admin
        self.client.force_authenticate(user=self.admin)
        
        # Valider l'exploitation
        response = self.client.post(
            f'/api/v1/farms/{self.exploitant.id}/verify',
            {
                'approved': True
            },
            format='json'
        )
        
        # Vérifier la réponse
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Exploitation vérifiée avec succès. Les fonctionnalités premium sont maintenant débloquées.'
        assert response.data['exploitant']['statut_verification'] == 'VERIFIE'
        assert response.data['exploitant']['premium_features_unlocked'] is True
        
        # Vérifier que le profil a été mis à jour
        self.exploitant_profile.refresh_from_db()
        assert self.exploitant_profile.statut_verification == 'VERIFIE'
        assert self.exploitant_profile.date_verification is not None
        assert self.exploitant_profile.motif_rejet is None
    
    def test_reject_farm_with_reason(self):
        """
        Test: Rejet d'une exploitation avec motif
        Exigence: 10.6
        """
        # Se connecter en tant qu'admin
        self.client.force_authenticate(user=self.admin)
        
        motif = "Documents justificatifs insuffisants. Veuillez fournir le titre foncier."
        
        # Rejeter l'exploitation
        response = self.client.post(
            f'/api/v1/farms/{self.exploitant.id}/verify',
            {
                'approved': False,
                'motif_rejet': motif
            },
            format='json'
        )
        
        # Vérifier la réponse
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Demande rejetée'
        assert response.data['exploitant']['statut_verification'] == 'REJETE'
        assert response.data['exploitant']['motif_rejet'] == motif
        
        # Vérifier que le profil a été mis à jour
        self.exploitant_profile.refresh_from_db()
        assert self.exploitant_profile.statut_verification == 'REJETE'
        assert self.exploitant_profile.motif_rejet == motif
        assert self.exploitant_profile.date_verification is not None
    
    def test_reject_without_reason_fails(self):
        """
        Test: Le rejet sans motif doit échouer
        Exigence: 10.6
        """
        # Se connecter en tant qu'admin
        self.client.force_authenticate(user=self.admin)
        
        # Tenter de rejeter sans motif
        response = self.client.post(
            f'/api/v1/farms/{self.exploitant.id}/verify',
            {
                'approved': False
            },
            format='json'
        )
        
        # Vérifier que la requête échoue
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'motif de rejet est requis' in response.data['error']
        
        # Vérifier que le profil n'a pas été modifié
        self.exploitant_profile.refresh_from_db()
        assert self.exploitant_profile.statut_verification == 'EN_ATTENTE'
    
    def test_non_admin_cannot_verify(self):
        """
        Test: Seuls les administrateurs peuvent vérifier les exploitations
        Exigence: 10.4
        """
        # Créer un utilisateur non-admin
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@test.com',
            phone_number='+22890000003',
            password='Test@123',
            user_type='ACHETEUR'
        )
        
        # Se connecter en tant qu'utilisateur régulier
        self.client.force_authenticate(user=regular_user)
        
        # Tenter de valider
        response = self.client.post(
            f'/api/v1/farms/{self.exploitant.id}/verify',
            {
                'approved': True
            },
            format='json'
        )
        
        # Vérifier que l'accès est refusé
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'Seuls les administrateurs' in response.data['error']
    
    def test_cannot_verify_already_verified_farm(self):
        """
        Test: Impossible de vérifier une exploitation déjà vérifiée
        Exigence: 10.4
        """
        # Marquer l'exploitation comme déjà vérifiée
        self.exploitant_profile.statut_verification = 'VERIFIE'
        self.exploitant_profile.save()
        
        # Se connecter en tant qu'admin
        self.client.force_authenticate(user=self.admin)
        
        # Tenter de vérifier à nouveau
        response = self.client.post(
            f'/api/v1/farms/{self.exploitant.id}/verify',
            {
                'approved': True
            },
            format='json'
        )
        
        # Vérifier que la requête échoue
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'déjà' in response.data['error']
    
    def test_get_pending_farms(self):
        """
        Test: Récupération de la liste des exploitations en attente
        """
        # Créer une deuxième exploitation en attente
        exploitant2 = User.objects.create_user(
            username='exploitant2',
            email='exploitant2@test.com',
            phone_number='+22890000004',
            password='Test@123',
            user_type='EXPLOITANT',
            first_name='Marie',
            last_name='Martin'
        )
        
        ExploitantProfile.objects.create(
            user=exploitant2,
            superficie_totale=20.0,
            canton_principal=self.canton,
            coordonnees_gps={'lat': 6.1320, 'lon': 1.2229},
            cultures_actuelles=['Riz'],
            statut_verification='EN_ATTENTE'
        )
        
        # Se connecter en tant qu'admin
        self.client.force_authenticate(user=self.admin)
        
        # Récupérer la liste
        response = self.client.get('/api/v1/farms/pending')
        
        # Vérifier la réponse
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        assert len(response.data['profiles']) == 2
        
        # Vérifier que les profils contiennent les bonnes informations
        profile_usernames = [p['username'] for p in response.data['profiles']]
        assert 'exploitant1' in profile_usernames
        assert 'exploitant2' in profile_usernames
    
    def test_get_farm_details(self):
        """
        Test: Récupération des détails complets d'une exploitation
        """
        # Se connecter en tant qu'admin
        self.client.force_authenticate(user=self.admin)
        
        # Récupérer les détails
        response = self.client.get(f'/api/v1/farms/{self.exploitant.id}/details')
        
        # Vérifier la réponse
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'exploitant1'
        assert response.data['first_name'] == 'Jean'
        assert response.data['last_name'] == 'Dupont'
        assert response.data['profile']['superficie_totale'] == '15.50'
        assert response.data['profile']['statut_verification'] == 'EN_ATTENTE'
        assert response.data['profile']['canton_principal']['nom'] == 'Lomé 1er'
        assert 'documents' in response.data
    
    def test_premium_features_unlocked_after_verification(self):
        """
        Test: Les fonctionnalités premium sont débloquées après vérification
        Exigence: 10.5
        """
        # Vérifier l'exploitation
        self.exploitant_profile.statut_verification = 'VERIFIE'
        self.exploitant_profile.save()
        
        # Se connecter en tant qu'exploitant
        self.client.force_authenticate(user=self.exploitant)
        
        # Récupérer les fonctionnalités premium
        response = self.client.get('/api/v1/farms/me/premium-features')
        
        # Vérifier que toutes les fonctionnalités sont débloquées
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_verified'] is True
        
        features = response.data['features']
        assert features['dashboard_avance']['enabled'] is True
        assert features['recrutement_agronomes']['enabled'] is True
        assert features['recrutement_ouvriers']['enabled'] is True
        assert features['prevente_agricole']['enabled'] is True
        assert features['analyses_marche']['enabled'] is True
        assert features['optimisation_logistique']['enabled'] is True
        assert features['recommandations_cultures']['enabled'] is True
        assert features['irrigation_intelligente']['enabled'] is True
    
    def test_premium_features_locked_when_not_verified(self):
        """
        Test: Les fonctionnalités premium sont bloquées si non vérifié
        Exigence: 10.5
        """
        # Se connecter en tant qu'exploitant (statut EN_ATTENTE)
        self.client.force_authenticate(user=self.exploitant)
        
        # Récupérer les fonctionnalités premium
        response = self.client.get('/api/v1/farms/me/premium-features')
        
        # Vérifier que toutes les fonctionnalités sont bloquées
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_verified'] is False
        
        features = response.data['features']
        assert features['dashboard_avance']['enabled'] is False
        assert features['recrutement_agronomes']['enabled'] is False
        assert features['recrutement_ouvriers']['enabled'] is False
        assert features['prevente_agricole']['enabled'] is False
        
        # Vérifier le message
        assert 'en cours de traitement' in response.data['message']


@pytest.mark.django_db
class TestFarmVerificationService(TestCase):
    """
    Tests unitaires pour le service FarmVerificationService
    """
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer les données géographiques
        self.region = Region.objects.create(nom='Maritime', code='MAR')
        self.prefecture = Prefecture.objects.create(
            nom='Golfe',
            code='GOL',
            region=self.region
        )
        self.canton = Canton.objects.create(
            nom='Lomé 1er',
            code='LOM1',
            prefecture=self.prefecture
        )
        
        # Créer un administrateur
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            phone_number='+22890000001',
            password='Admin@123',
            user_type='ADMIN',
            is_staff=True
        )
        
        # Créer un exploitant
        self.exploitant = User.objects.create_user(
            username='exploitant1',
            email='exploitant1@test.com',
            phone_number='+22890000002',
            password='Test@123',
            user_type='EXPLOITANT'
        )
        
        self.exploitant_profile = ExploitantProfile.objects.create(
            user=self.exploitant,
            superficie_totale=15.5,
            canton_principal=self.canton,
            coordonnees_gps={'lat': 6.1319, 'lon': 1.2228},
            statut_verification='EN_ATTENTE'
        )
    
    def test_service_verify_farm_success(self):
        """
        Test: Le service valide correctement une exploitation
        """
        result = FarmVerificationService.verify_farm(
            exploitant_profile=self.exploitant_profile,
            admin_user=self.admin,
            approved=True
        )
        
        assert result['success'] is True
        assert 'vérifiée avec succès' in result['message']
        assert result['exploitant']['statut_verification'] == 'VERIFIE'
        assert result['exploitant']['premium_features_unlocked'] is True
    
    def test_service_reject_farm_with_reason(self):
        """
        Test: Le service rejette correctement une exploitation avec motif
        """
        motif = "Superficie déclarée non cohérente avec les documents"
        
        result = FarmVerificationService.verify_farm(
            exploitant_profile=self.exploitant_profile,
            admin_user=self.admin,
            approved=False,
            motif_rejet=motif
        )
        
        assert result['success'] is True
        assert result['message'] == 'Demande rejetée'
        assert result['exploitant']['statut_verification'] == 'REJETE'
        assert result['exploitant']['motif_rejet'] == motif
    
    def test_service_requires_admin(self):
        """
        Test: Le service vérifie que l'utilisateur est admin
        """
        # Créer un utilisateur non-admin
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@test.com',
            phone_number='+22890000003',
            password='Test@123',
            user_type='ACHETEUR'
        )
        
        result = FarmVerificationService.verify_farm(
            exploitant_profile=self.exploitant_profile,
            admin_user=regular_user,
            approved=True
        )
        
        assert result['success'] is False
        assert 'administrateurs' in result['error']
    
    def test_service_get_pending_verifications(self):
        """
        Test: Le service récupère correctement les exploitations en attente
        """
        # Créer une deuxième exploitation en attente
        exploitant2 = User.objects.create_user(
            username='exploitant2',
            email='exploitant2@test.com',
            phone_number='+22890000004',
            password='Test@123',
            user_type='EXPLOITANT'
        )
        
        ExploitantProfile.objects.create(
            user=exploitant2,
            superficie_totale=20.0,
            canton_principal=self.canton,
            coordonnees_gps={'lat': 6.1320, 'lon': 1.2229},
            statut_verification='EN_ATTENTE'
        )
        
        result = FarmVerificationService.get_pending_verifications()
        
        assert result['success'] is True
        assert result['count'] == 2
        assert len(result['profiles']) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
