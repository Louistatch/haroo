"""
Tests pour la validation administrative des agronomes
Exigences: 7.5, 7.6
"""
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User, AgronomeProfile
from apps.locations.models import Region, Prefecture, Canton
from apps.users.services import ValidationWorkflowService
from django.utils import timezone


@pytest.mark.django_db
class TestAgronomeValidation(TestCase):
    """Tests pour la validation administrative des agronomes"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.client = APIClient()
        
        # Créer les données géographiques de test
        self.region = Region.objects.create(
            nom="Région Maritime",
            code="MAR"
        )
        self.prefecture = Prefecture.objects.create(
            nom="Golfe",
            code="GOL",
            region=self.region
        )
        self.canton = Canton.objects.create(
            nom="Lomé 1er",
            code="LOM1",
            prefecture=self.prefecture
        )
        
        # Créer un administrateur
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            phone_number='+22890000001',
            password='AdminPass123!',
            user_type='ADMIN',
            is_staff=True,
            is_superuser=True
        )
        
        # Créer un utilisateur non-admin
        self.regular_user = User.objects.create_user(
            username='user_test',
            email='user@test.com',
            phone_number='+22890000002',
            password='UserPass123!',
            user_type='EXPLOITANT'
        )
        
        # Créer un agronome en attente de validation
        self.agronome_user = User.objects.create_user(
            username='agronome_test',
            email='agronome@test.com',
            phone_number='+22890000003',
            password='AgroPass123!',
            first_name='Jean',
            last_name='Dupont',
            user_type='AGRONOME'
        )
        
        self.agronome_profile = AgronomeProfile.objects.create(
            user=self.agronome_user,
            canton_rattachement=self.canton,
            specialisations=['Maraîchage', 'Céréaliculture'],
            statut_validation='EN_ATTENTE'
        )
    
    def test_validate_agronomist_success(self):
        """
        Test de validation réussie d'un agronome
        Exigence 7.5: Statut VALIDE + Badge Agronome_Validé
        """
        # Authentifier l'admin
        self.client.force_authenticate(user=self.admin_user)
        
        # URL de validation
        url = reverse('users:validate-agronomist', kwargs={'agronomist_id': self.agronome_user.id})
        
        # Données de validation
        data = {
            'approved': True
        }
        
        # Effectuer la requête
        response = self.client.post(url, data, format='json')
        
        # Vérifications
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Agronome validé avec succès'
        assert response.data['agronome']['statut_validation'] == 'VALIDE'
        assert response.data['agronome']['badge_valide'] is True
        assert 'date_validation' in response.data['agronome']
        
        # Vérifier en base de données
        self.agronome_profile.refresh_from_db()
        assert self.agronome_profile.statut_validation == 'VALIDE'
        assert self.agronome_profile.badge_valide is True
        assert self.agronome_profile.date_validation is not None
        assert self.agronome_profile.motif_rejet is None
    
    def test_reject_agronomist_with_reason(self):
        """
        Test de rejet d'un agronome avec motif
        Exigence 7.6: Statut REJETE + Notification avec motif
        """
        # Authentifier l'admin
        self.client.force_authenticate(user=self.admin_user)
        
        # URL de validation
        url = reverse('users:validate-agronomist', kwargs={'agronomist_id': self.agronome_user.id})
        
        # Données de rejet
        motif = "Documents justificatifs incomplets. Veuillez fournir votre diplôme d'agronomie."
        data = {
            'approved': False,
            'motif_rejet': motif
        }
        
        # Effectuer la requête
        response = self.client.post(url, data, format='json')
        
        # Vérifications
        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Demande rejetée'
        assert response.data['agronome']['statut_validation'] == 'REJETE'
        assert response.data['agronome']['badge_valide'] is False
        assert response.data['agronome']['motif_rejet'] == motif
        
        # Vérifier en base de données
        self.agronome_profile.refresh_from_db()
        assert self.agronome_profile.statut_validation == 'REJETE'
        assert self.agronome_profile.badge_valide is False
        assert self.agronome_profile.motif_rejet == motif
        assert self.agronome_profile.date_validation is not None
    
    def test_reject_without_reason_fails(self):
        """
        Test que le rejet sans motif échoue
        Exigence 7.6: Motif requis pour le rejet
        """
        # Authentifier l'admin
        self.client.force_authenticate(user=self.admin_user)
        
        # URL de validation
        url = reverse('users:validate-agronomist', kwargs={'agronomist_id': self.agronome_user.id})
        
        # Données de rejet sans motif
        data = {
            'approved': False
        }
        
        # Effectuer la requête
        response = self.client.post(url, data, format='json')
        
        # Vérifications
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'motif de rejet est requis' in response.data['error']
        
        # Vérifier que le statut n'a pas changé
        self.agronome_profile.refresh_from_db()
        assert self.agronome_profile.statut_validation == 'EN_ATTENTE'
    
    def test_non_admin_cannot_validate(self):
        """
        Test qu'un utilisateur non-admin ne peut pas valider
        """
        # Authentifier un utilisateur régulier
        self.client.force_authenticate(user=self.regular_user)
        
        # URL de validation
        url = reverse('users:validate-agronomist', kwargs={'agronomist_id': self.agronome_user.id})
        
        # Données de validation
        data = {
            'approved': True
        }
        
        # Effectuer la requête
        response = self.client.post(url, data, format='json')
        
        # Vérifications
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'Accès refusé' in response.data['error']
        
        # Vérifier que le statut n'a pas changé
        self.agronome_profile.refresh_from_db()
        assert self.agronome_profile.statut_validation == 'EN_ATTENTE'
    
    def test_cannot_validate_already_validated_profile(self):
        """
        Test qu'on ne peut pas valider un profil déjà validé
        """
        # Valider le profil d'abord
        self.agronome_profile.statut_validation = 'VALIDE'
        self.agronome_profile.badge_valide = True
        self.agronome_profile.date_validation = timezone.now()
        self.agronome_profile.save()
        
        # Authentifier l'admin
        self.client.force_authenticate(user=self.admin_user)
        
        # URL de validation
        url = reverse('users:validate-agronomist', kwargs={'agronomist_id': self.agronome_user.id})
        
        # Données de validation
        data = {
            'approved': True
        }
        
        # Effectuer la requête
        response = self.client.post(url, data, format='json')
        
        # Vérifications
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'déjà' in response.data['error']
    
    def test_get_pending_agronomists(self):
        """
        Test de récupération des agronomes en attente
        """
        # Créer un deuxième agronome en attente
        agronome_user2 = User.objects.create_user(
            username='agronome_test2',
            email='agronome2@test.com',
            phone_number='+22890000004',
            password='AgroPass123!',
            first_name='Marie',
            last_name='Martin',
            user_type='AGRONOME'
        )
        
        AgronomeProfile.objects.create(
            user=agronome_user2,
            canton_rattachement=self.canton,
            specialisations=['Arboriculture'],
            statut_validation='EN_ATTENTE'
        )
        
        # Créer un agronome déjà validé (ne doit pas apparaître)
        agronome_user3 = User.objects.create_user(
            username='agronome_test3',
            email='agronome3@test.com',
            phone_number='+22890000005',
            password='AgroPass123!',
            user_type='AGRONOME'
        )
        
        AgronomeProfile.objects.create(
            user=agronome_user3,
            canton_rattachement=self.canton,
            specialisations=['Élevage'],
            statut_validation='VALIDE',
            badge_valide=True
        )
        
        # Authentifier l'admin
        self.client.force_authenticate(user=self.admin_user)
        
        # URL de la liste
        url = reverse('users:get-pending-agronomists')
        
        # Effectuer la requête
        response = self.client.get(url)
        
        # Vérifications
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2  # Seulement les 2 en attente
        assert len(response.data['profiles']) == 2
        
        # Vérifier que les profils en attente sont présents
        usernames = [p['username'] for p in response.data['profiles']]
        assert 'agronome_test' in usernames
        assert 'agronome_test2' in usernames
        assert 'agronome_test3' not in usernames  # Le validé ne doit pas apparaître
    
    def test_get_agronomist_details(self):
        """
        Test de récupération des détails d'un agronome
        """
        # Authentifier l'admin
        self.client.force_authenticate(user=self.admin_user)
        
        # URL des détails
        url = reverse('users:get-agronomist-details', kwargs={'agronomist_id': self.agronome_user.id})
        
        # Effectuer la requête
        response = self.client.get(url)
        
        # Vérifications
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == self.agronome_user.id
        assert response.data['username'] == 'agronome_test'
        assert response.data['first_name'] == 'Jean'
        assert response.data['last_name'] == 'Dupont'
        assert response.data['profile']['statut_validation'] == 'EN_ATTENTE'
        assert response.data['profile']['canton_rattachement']['nom'] == 'Lomé 1er'
        assert 'Maraîchage' in response.data['profile']['specialisations']
        assert 'documents' in response.data
    
    def test_validation_workflow_service_validate(self):
        """
        Test du service ValidationWorkflowService pour validation
        """
        result = ValidationWorkflowService.validate_agronomist(
            agronome_profile=self.agronome_profile,
            admin_user=self.admin_user,
            approved=True
        )
        
        assert result['success'] is True
        assert result['message'] == 'Agronome validé avec succès'
        assert result['agronome']['statut_validation'] == 'VALIDE'
        assert result['agronome']['badge_valide'] is True
        
        # Vérifier en base de données
        self.agronome_profile.refresh_from_db()
        assert self.agronome_profile.statut_validation == 'VALIDE'
        assert self.agronome_profile.badge_valide is True
    
    def test_validation_workflow_service_reject(self):
        """
        Test du service ValidationWorkflowService pour rejet
        """
        motif = "Documents non conformes"
        
        result = ValidationWorkflowService.validate_agronomist(
            agronome_profile=self.agronome_profile,
            admin_user=self.admin_user,
            approved=False,
            motif_rejet=motif
        )
        
        assert result['success'] is True
        assert result['message'] == 'Demande rejetée'
        assert result['agronome']['statut_validation'] == 'REJETE'
        assert result['agronome']['badge_valide'] is False
        assert result['agronome']['motif_rejet'] == motif
        
        # Vérifier en base de données
        self.agronome_profile.refresh_from_db()
        assert self.agronome_profile.statut_validation == 'REJETE'
        assert self.agronome_profile.motif_rejet == motif
    
    def test_validation_workflow_service_non_admin_fails(self):
        """
        Test que le service refuse la validation par un non-admin
        """
        result = ValidationWorkflowService.validate_agronomist(
            agronome_profile=self.agronome_profile,
            admin_user=self.regular_user,
            approved=True
        )
        
        assert result['success'] is False
        assert 'administrateurs' in result['error']
        
        # Vérifier que le statut n'a pas changé
        self.agronome_profile.refresh_from_db()
        assert self.agronome_profile.statut_validation == 'EN_ATTENTE'
    
    def test_get_pending_validations_service(self):
        """
        Test du service get_pending_validations
        """
        result = ValidationWorkflowService.get_pending_validations()
        
        assert result['success'] is True
        assert result['count'] == 1
        assert len(result['profiles']) == 1
        assert result['profiles'][0]['username'] == 'agronome_test'
        assert 'nombre_documents' in result['profiles'][0]
    
    def test_missing_approved_parameter(self):
        """
        Test que le paramètre approved est requis
        """
        # Authentifier l'admin
        self.client.force_authenticate(user=self.admin_user)
        
        # URL de validation
        url = reverse('users:validate-agronomist', kwargs={'agronomist_id': self.agronome_user.id})
        
        # Données sans le paramètre approved
        data = {}
        
        # Effectuer la requête
        response = self.client.post(url, data, format='json')
        
        # Vérifications
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'approved' in response.data['error']
    
    def test_invalid_agronomist_id(self):
        """
        Test avec un ID d'agronome invalide
        """
        # Authentifier l'admin
        self.client.force_authenticate(user=self.admin_user)
        
        # URL avec un ID inexistant
        url = reverse('users:validate-agronomist', kwargs={'agronomist_id': 99999})
        
        # Données de validation
        data = {
            'approved': True
        }
        
        # Effectuer la requête
        response = self.client.post(url, data, format='json')
        
        # Vérifications
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'non trouvé' in response.data['error']
