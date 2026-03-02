"""
Tests pour le système de missions
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.locations.models import Region, Prefecture, Canton
from apps.users.models import ExploitantProfile, AgronomeProfile
from .models import Mission

User = get_user_model()


class MissionModelTest(TestCase):
    """Tests pour le modèle Mission"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer les données géographiques
        self.region = Region.objects.create(nom="Maritime", code="MAR")
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
        
        # Créer un exploitant vérifié
        self.exploitant_user = User.objects.create_user(
            username='exploitant',
            phone_number='+22890123456',
            password='testpass123',
            user_type='EXPLOITANT'
        )
        from django.contrib.gis.geos import Point
        self.exploitant_profile = ExploitantProfile.objects.create(
            user=self.exploitant_user,
            superficie_totale=Decimal('15.00'),
            canton_principal=self.canton,
            coordonnees_gps=Point(1.2, 6.1),
            statut_verification='VERIFIE'
        )
        
        # Créer un agronome validé
        self.agronome_user = User.objects.create_user(
            username='agronome',
            phone_number='+22890123457',
            password='testpass123',
            user_type='AGRONOME'
        )
        self.agronome_profile = AgronomeProfile.objects.create(
            user=self.agronome_user,
            canton_rattachement=self.canton,
            statut_validation='VALIDE',
            badge_valide=True
        )
    
    def test_create_mission(self):
        """Test de création d'une mission"""
        mission = Mission.objects.create(
            exploitant=self.exploitant_user,
            agronome=self.agronome_user,
            description="Conseil pour la culture du maïs",
            budget_propose=Decimal('50000.00')
        )
        
        self.assertEqual(mission.statut, 'DEMANDE')
        self.assertEqual(mission.exploitant, self.exploitant_user)
        self.assertEqual(mission.agronome, self.agronome_user)
        self.assertEqual(mission.budget_propose, Decimal('50000.00'))
    
    def test_mission_str(self):
        """Test de la représentation string d'une mission"""
        mission = Mission.objects.create(
            exploitant=self.exploitant_user,
            agronome=self.agronome_user,
            description="Test mission",
            budget_propose=Decimal('50000.00')
        )
        
        self.assertIn(str(mission.id), str(mission))
        self.assertIn(self.exploitant_user.get_full_name(), str(mission))
        self.assertIn(self.agronome_user.get_full_name(), str(mission))


class MissionAPITest(APITestCase):
    """Tests pour l'API des missions"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer les données géographiques
        self.region = Region.objects.create(nom="Maritime", code="MAR")
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
        
        # Créer un exploitant vérifié
        self.exploitant_user = User.objects.create_user(
            username='exploitant',
            phone_number='+22890123456',
            password='testpass123',
            user_type='EXPLOITANT',
            first_name='Jean',
            last_name='Dupont'
        )
        from django.contrib.gis.geos import Point
        self.exploitant_profile = ExploitantProfile.objects.create(
            user=self.exploitant_user,
            superficie_totale=Decimal('15.00'),
            canton_principal=self.canton,
            coordonnees_gps=Point(1.2, 6.1),
            statut_verification='VERIFIE'
        )
        
        # Créer un agronome validé
        self.agronome_user = User.objects.create_user(
            username='agronome',
            phone_number='+22890123457',
            password='testpass123',
            user_type='AGRONOME',
            first_name='Marie',
            last_name='Martin'
        )
        self.agronome_profile = AgronomeProfile.objects.create(
            user=self.agronome_user,
            canton_rattachement=self.canton,
            statut_validation='VALIDE',
            badge_valide=True
        )
        
        # Créer un exploitant non vérifié
        self.exploitant_non_verifie = User.objects.create_user(
            username='exploitant_nv',
            phone_number='+22890123458',
            password='testpass123',
            user_type='EXPLOITANT'
        )
        ExploitantProfile.objects.create(
            user=self.exploitant_non_verifie,
            superficie_totale=Decimal('15.00'),
            canton_principal=self.canton,
            coordonnees_gps=Point(1.2, 6.1),
            statut_verification='NON_VERIFIE'
        )
    
    def test_create_mission_success(self):
        """Test de création d'une mission avec succès"""
        self.client.force_authenticate(user=self.exploitant_user)
        
        data = {
            'agronome': self.agronome_user.id,
            'description': 'Conseil pour la culture du maïs',
            'budget_propose': '50000.00'
        }
        
        response = self.client.post('/api/v1/missions/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['statut'], 'DEMANDE')
        self.assertEqual(response.data['exploitant'], self.exploitant_user.id)
        self.assertEqual(response.data['agronome'], self.agronome_user.id)
        
        # Vérifier que la mission a été créée en base
        self.assertEqual(Mission.objects.count(), 1)
        mission = Mission.objects.first()
        self.assertEqual(mission.exploitant, self.exploitant_user)
        self.assertEqual(mission.agronome, self.agronome_user)
    
    def test_create_mission_exploitant_non_verifie(self):
        """Test de création d'une mission par un exploitant non vérifié"""
        self.client.force_authenticate(user=self.exploitant_non_verifie)
        
        data = {
            'agronome': self.agronome_user.id,
            'description': 'Conseil pour la culture du maïs',
            'budget_propose': '50000.00'
        }
        
        response = self.client.post('/api/v1/missions/', data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Mission.objects.count(), 0)
    
    def test_create_mission_budget_negatif(self):
        """Test de création d'une mission avec un budget négatif"""
        self.client.force_authenticate(user=self.exploitant_user)
        
        data = {
            'agronome': self.agronome_user.id,
            'description': 'Conseil pour la culture du maïs',
            'budget_propose': '-50000.00'
        }
        
        response = self.client.post('/api/v1/missions/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('budget_propose', response.data)
    
    def test_accept_mission_success(self):
        """Test d'acceptation d'une mission avec succès"""
        # Créer une mission
        mission = Mission.objects.create(
            exploitant=self.exploitant_user,
            agronome=self.agronome_user,
            description="Conseil pour la culture du maïs",
            budget_propose=Decimal('50000.00')
        )
        
        # L'agronome accepte la mission
        self.client.force_authenticate(user=self.agronome_user)
        response = self.client.post(f'/api/v1/missions/{mission.id}/accept/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['statut'], 'ACCEPTEE')
        
        # Vérifier en base
        mission.refresh_from_db()
        self.assertEqual(mission.statut, 'ACCEPTEE')
    
    def test_accept_mission_wrong_user(self):
        """Test d'acceptation d'une mission par un mauvais utilisateur"""
        # Créer une mission
        mission = Mission.objects.create(
            exploitant=self.exploitant_user,
            agronome=self.agronome_user,
            description="Conseil pour la culture du maïs",
            budget_propose=Decimal('50000.00')
        )
        
        # L'exploitant essaie d'accepter la mission (devrait échouer)
        self.client.force_authenticate(user=self.exploitant_user)
        response = self.client.post(f'/api/v1/missions/{mission.id}/accept/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Vérifier que le statut n'a pas changé
        mission.refresh_from_db()
        self.assertEqual(mission.statut, 'DEMANDE')
    
    def test_accept_mission_invalid_status(self):
        """Test d'acceptation d'une mission avec un statut invalide"""
        # Créer une mission déjà acceptée
        mission = Mission.objects.create(
            exploitant=self.exploitant_user,
            agronome=self.agronome_user,
            description="Conseil pour la culture du maïs",
            budget_propose=Decimal('50000.00'),
            statut='ACCEPTEE'
        )
        
        # L'agronome essaie d'accepter à nouveau
        self.client.force_authenticate(user=self.agronome_user)
        response = self.client.post(f'/api/v1/missions/{mission.id}/accept/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_complete_mission_success(self):
        """Test de complétion d'une mission avec succès"""
        # Créer une mission acceptée
        mission = Mission.objects.create(
            exploitant=self.exploitant_user,
            agronome=self.agronome_user,
            description="Conseil pour la culture du maïs",
            budget_propose=Decimal('50000.00'),
            statut='ACCEPTEE'
        )
        
        # L'exploitant marque la mission comme terminée
        self.client.force_authenticate(user=self.exploitant_user)
        response = self.client.post(f'/api/v1/missions/{mission.id}/complete/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['statut'], 'TERMINEE')
        
        # Vérifier en base
        mission.refresh_from_db()
        self.assertEqual(mission.statut, 'TERMINEE')
    
    def test_complete_mission_wrong_user(self):
        """Test de complétion d'une mission par un mauvais utilisateur"""
        # Créer une mission acceptée
        mission = Mission.objects.create(
            exploitant=self.exploitant_user,
            agronome=self.agronome_user,
            description="Conseil pour la culture du maïs",
            budget_propose=Decimal('50000.00'),
            statut='ACCEPTEE'
        )
        
        # L'agronome essaie de marquer la mission comme terminée (devrait échouer)
        self.client.force_authenticate(user=self.agronome_user)
        response = self.client.post(f'/api/v1/missions/{mission.id}/complete/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Vérifier que le statut n'a pas changé
        mission.refresh_from_db()
        self.assertEqual(mission.statut, 'ACCEPTEE')
    
    def test_complete_mission_invalid_status(self):
        """Test de complétion d'une mission avec un statut invalide"""
        # Créer une mission en statut DEMANDE
        mission = Mission.objects.create(
            exploitant=self.exploitant_user,
            agronome=self.agronome_user,
            description="Conseil pour la culture du maïs",
            budget_propose=Decimal('50000.00'),
            statut='DEMANDE'
        )
        
        # L'exploitant essaie de marquer la mission comme terminée
        self.client.force_authenticate(user=self.exploitant_user)
        response = self.client.post(f'/api/v1/missions/{mission.id}/complete/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_missions_exploitant(self):
        """Test de listage des missions pour un exploitant"""
        # Créer plusieurs missions
        Mission.objects.create(
            exploitant=self.exploitant_user,
            agronome=self.agronome_user,
            description="Mission 1",
            budget_propose=Decimal('50000.00')
        )
        Mission.objects.create(
            exploitant=self.exploitant_user,
            agronome=self.agronome_user,
            description="Mission 2",
            budget_propose=Decimal('60000.00')
        )
        
        # L'exploitant liste ses missions
        self.client.force_authenticate(user=self.exploitant_user)
        response = self.client.get('/api/v1/missions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_list_missions_agronome(self):
        """Test de listage des missions pour un agronome"""
        # Créer plusieurs missions
        Mission.objects.create(
            exploitant=self.exploitant_user,
            agronome=self.agronome_user,
            description="Mission 1",
            budget_propose=Decimal('50000.00')
        )
        Mission.objects.create(
            exploitant=self.exploitant_user,
            agronome=self.agronome_user,
            description="Mission 2",
            budget_propose=Decimal('60000.00')
        )
        
        # L'agronome liste ses missions
        self.client.force_authenticate(user=self.agronome_user)
        response = self.client.get('/api/v1/missions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_retrieve_mission_detail(self):
        """Test de récupération des détails d'une mission"""
        mission = Mission.objects.create(
            exploitant=self.exploitant_user,
            agronome=self.agronome_user,
            description="Conseil pour la culture du maïs",
            budget_propose=Decimal('50000.00')
        )
        
        # L'exploitant récupère les détails
        self.client.force_authenticate(user=self.exploitant_user)
        response = self.client.get(f'/api/v1/missions/{mission.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], mission.id)
        self.assertEqual(response.data['description'], mission.description)
        self.assertIn('exploitant_nom', response.data)
        self.assertIn('agronome_nom', response.data)
