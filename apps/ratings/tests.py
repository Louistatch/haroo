"""
Tests pour le système de notation
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from apps.locations.models import Region, Prefecture, Canton
from apps.missions.models import Mission
from apps.payments.models import Transaction
from .models import Notation, SignalementNotation
from .services import ReputationCalculator, QualityAlertService

User = get_user_model()


class NotationModelTest(TestCase):
    """Tests pour le modèle Notation"""
    
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
        self.exploitant = User.objects.create_user(
            username='exploitant@test.com',
            email='exploitant@test.com',
            password='Test1234!',
            phone_number='+22890123456',
            user_type='EXPLOITANT',
            first_name='Jean',
            last_name='Dupont'
        )
        from apps.users.models import ExploitantProfile
        from django.contrib.gis.geos import Point
        self.exploitant_profile = ExploitantProfile.objects.create(
            user=self.exploitant,
            superficie_totale=Decimal('15.00'),
            canton_principal=self.canton,
            coordonnees_gps=Point(1.2, 6.1),  # Coordonnées GPS de Lomé
            statut_verification='VERIFIE'
        )
        
        # Créer un agronome validé
        self.agronome = User.objects.create_user(
            username='agronome@test.com',
            email='agronome@test.com',
            password='Test1234!',
            phone_number='+22890123457',
            user_type='AGRONOME',
            first_name='Marie',
            last_name='Martin'
        )
        from apps.users.models import AgronomeProfile
        self.agronome_profile = AgronomeProfile.objects.create(
            user=self.agronome,
            canton_rattachement=self.canton,
            specialisations=['Maraîchage', 'Irrigation'],
            statut_validation='VALIDE',
            badge_valide=True
        )
        
        # Créer une transaction
        self.transaction = Transaction.objects.create(
            utilisateur=self.exploitant,
            type_transaction='RECRUTEMENT_AGRONOME',
            montant=Decimal('50000.00'),
            commission_plateforme=Decimal('5000.00'),
            statut='SUCCESS'
        )
        
        # Créer une mission terminée
        self.mission = Mission.objects.create(
            exploitant=self.exploitant,
            agronome=self.agronome,
            description="Mission de conseil agricole",
            budget_propose=Decimal('50000.00'),
            statut='TERMINEE',
            transaction=self.transaction
        )
    
    def test_create_notation_valid(self):
        """Test: Créer une notation valide (Exigences 27.1, 27.2)"""
        notation = Notation.objects.create(
            notateur=self.exploitant,
            note=self.agronome,
            note_valeur=5,
            commentaire="Excellent travail, très professionnel et compétent.",
            mission=self.mission
        )
        
        self.assertEqual(notation.note_valeur, 5)
        self.assertEqual(notation.statut, 'PUBLIE')
        self.assertEqual(notation.nombre_signalements, 0)
    
    def test_notation_rating_validation(self):
        """Test: Validation de la note (1-5 étoiles) (Exigence 27.1)"""
        # Note trop basse
        with self.assertRaises(ValidationError):
            notation = Notation(
                notateur=self.exploitant,
                note=self.agronome,
                note_valeur=0,
                commentaire="Commentaire de test avec plus de 20 caractères",
                mission=self.mission
            )
            notation.full_clean()
        
        # Note trop haute
        with self.assertRaises(ValidationError):
            notation = Notation(
                notateur=self.exploitant,
                note=self.agronome,
                note_valeur=6,
                commentaire="Commentaire de test avec plus de 20 caractères",
                mission=self.mission
            )
            notation.full_clean()
    
    def test_notation_comment_min_length(self):
        """Test: Commentaire minimum 20 caractères (Exigence 27.2)"""
        with self.assertRaises(ValidationError):
            notation = Notation(
                notateur=self.exploitant,
                note=self.agronome,
                note_valeur=5,
                commentaire="Trop court",  # Moins de 20 caractères
                mission=self.mission
            )
            notation.full_clean()
    
    def test_notation_requires_completed_mission(self):
        """Test: Notation uniquement après mission terminée"""
        # Créer une mission en cours
        mission_en_cours = Mission.objects.create(
            exploitant=self.exploitant,
            agronome=self.agronome,
            description="Mission en cours",
            budget_propose=Decimal('30000.00'),
            statut='EN_COURS'
        )
        
        notation = Notation(
            notateur=self.exploitant,
            note=self.agronome,
            note_valeur=5,
            commentaire="Commentaire de test avec plus de 20 caractères",
            mission=mission_en_cours
        )
        
        with self.assertRaises(ValidationError):
            notation.clean()
    
    def test_notation_participant_validation(self):
        """Test: Seuls les participants peuvent noter"""
        # Créer un autre utilisateur
        autre_user = User.objects.create_user(
            username='autre@test.com',
            email='autre@test.com',
            password='Test1234!',
            phone_number='+22890123458',
            user_type='ACHETEUR'
        )
        
        notation = Notation(
            notateur=autre_user,
            note=self.agronome,
            note_valeur=5,
            commentaire="Commentaire de test avec plus de 20 caractères",
            mission=self.mission
        )
        
        with self.assertRaises(ValidationError):
            notation.clean()
    
    def test_notation_no_self_rating(self):
        """Test: Impossible de se noter soi-même"""
        notation = Notation(
            notateur=self.agronome,
            note=self.agronome,
            note_valeur=5,
            commentaire="Commentaire de test avec plus de 20 caractères",
            mission=self.mission
        )
        
        with self.assertRaises(ValidationError):
            notation.clean()
    
    def test_notation_unique_per_mission(self):
        """Test: Une seule notation par utilisateur par mission"""
        # Créer une première notation
        Notation.objects.create(
            notateur=self.exploitant,
            note=self.agronome,
            note_valeur=5,
            commentaire="Première notation avec plus de 20 caractères",
            mission=self.mission
        )
        
        # Tenter de créer une deuxième notation
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Notation.objects.create(
                notateur=self.exploitant,
                note=self.agronome,
                note_valeur=4,
                commentaire="Deuxième notation avec plus de 20 caractères",
                mission=self.mission
            )


class ReputationCalculatorTest(TestCase):
    """Tests pour le calcul de réputation"""
    
    def setUp(self):
        """Configuration initiale"""
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
        
        # Créer un agronome
        self.agronome = User.objects.create_user(
            username='agronome@test.com',
            email='agronome@test.com',
            password='Test1234!',
            phone_number='+22890123457',
            user_type='AGRONOME',
            first_name='Marie',
            last_name='Martin'
        )
        from apps.users.models import AgronomeProfile
        self.agronome_profile = AgronomeProfile.objects.create(
            user=self.agronome,
            canton_rattachement=self.canton,
            specialisations=['Maraîchage'],
            statut_validation='VALIDE',
            badge_valide=True
        )
    
    def test_calculate_average_rating(self):
        """Test: Calcul de la note moyenne avec 2 décimales (Exigence 27.3)"""
        # Créer des notations simulées
        exploitant1 = User.objects.create_user(
            username='exp1@test.com',
            password='Test1234!',
            phone_number='+22890123456',
            user_type='EXPLOITANT'
        )
        exploitant2 = User.objects.create_user(
            username='exp2@test.com',
            password='Test1234!',
            phone_number='+22890123458',
            user_type='EXPLOITANT'
        )
        
        # Créer des missions terminées
        from apps.users.models import ExploitantProfile
        from django.contrib.gis.geos import Point
        for exp in [exploitant1, exploitant2]:
            ExploitantProfile.objects.create(
                user=exp,
                superficie_totale=Decimal('15.00'),
                canton_principal=self.canton,
                coordonnees_gps=Point(1.2, 6.1),
                statut_verification='VERIFIE'
            )
        
        mission1 = Mission.objects.create(
            exploitant=exploitant1,
            agronome=self.agronome,
            description="Mission 1",
            budget_propose=Decimal('50000.00'),
            statut='TERMINEE'
        )
        mission2 = Mission.objects.create(
            exploitant=exploitant2,
            agronome=self.agronome,
            description="Mission 2",
            budget_propose=Decimal('50000.00'),
            statut='TERMINEE'
        )
        
        # Créer des notations
        Notation.objects.create(
            notateur=exploitant1,
            note=self.agronome,
            note_valeur=5,
            commentaire="Excellent travail, très professionnel et compétent.",
            mission=mission1,
            statut='PUBLIE'
        )
        Notation.objects.create(
            notateur=exploitant2,
            note=self.agronome,
            note_valeur=4,
            commentaire="Bon travail dans l'ensemble, quelques améliorations possibles.",
            mission=mission2,
            statut='PUBLIE'
        )
        
        # Calculer la note moyenne
        moyenne, nombre = ReputationCalculator.update_user_rating(self.agronome)
        
        # Vérifier: (5 + 4) / 2 = 4.5
        self.assertEqual(moyenne, Decimal('4.50'))
        self.assertEqual(nombre, 2)
        
        # Vérifier que le profil a été mis à jour
        self.agronome_profile.refresh_from_db()
        self.assertEqual(self.agronome_profile.note_moyenne, Decimal('4.50'))
        self.assertEqual(self.agronome_profile.nombre_avis, 2)


class NotationAPITest(APITestCase):
    """Tests pour l'API de notation"""
    
    def setUp(self):
        """Configuration initiale"""
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
        self.exploitant = User.objects.create_user(
            username='exploitant@test.com',
            email='exploitant@test.com',
            password='Test1234!',
            phone_number='+22890123456',
            user_type='EXPLOITANT'
        )
        from apps.users.models import ExploitantProfile
        from django.contrib.gis.geos import Point
        ExploitantProfile.objects.create(
            user=self.exploitant,
            superficie_totale=Decimal('15.00'),
            canton_principal=self.canton,
            coordonnees_gps=Point(1.2, 6.1),
            statut_verification='VERIFIE'
        )
        
        # Créer un agronome validé
        self.agronome = User.objects.create_user(
            username='agronome@test.com',
            email='agronome@test.com',
            password='Test1234!',
            phone_number='+22890123457',
            user_type='AGRONOME'
        )
        from apps.users.models import AgronomeProfile
        AgronomeProfile.objects.create(
            user=self.agronome,
            canton_rattachement=self.canton,
            specialisations=['Maraîchage'],
            statut_validation='VALIDE',
            badge_valide=True
        )
        
        # Créer une mission terminée
        self.mission = Mission.objects.create(
            exploitant=self.exploitant,
            agronome=self.agronome,
            description="Mission de test",
            budget_propose=Decimal('50000.00'),
            statut='TERMINEE'
        )
    
    def test_create_notation_api(self):
        """Test: Créer une notation via l'API"""
        self.client.force_authenticate(user=self.exploitant)
        
        data = {
            'note_valeur': 5,
            'commentaire': 'Excellent travail, très professionnel et compétent.',
            'mission': self.mission.id
        }
        
        response = self.client.post('/api/v1/ratings/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['note_valeur'], 5)
        self.assertEqual(response.data['statut'], 'PUBLIE')
    
    def test_create_notation_invalid_rating(self):
        """Test: Validation de la note invalide"""
        self.client.force_authenticate(user=self.exploitant)
        
        data = {
            'note_valeur': 6,  # Invalide
            'commentaire': 'Commentaire de test avec plus de 20 caractères',
            'mission': self.mission.id
        }
        
        response = self.client.post('/api/v1/ratings/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_notation_short_comment(self):
        """Test: Commentaire trop court"""
        self.client.force_authenticate(user=self.exploitant)
        
        data = {
            'note_valeur': 5,
            'commentaire': 'Trop court',  # Moins de 20 caractères
            'mission': self.mission.id
        }
        
        response = self.client.post('/api/v1/ratings/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_notations_with_filters(self):
        """Test: Lister les notations avec filtres (Exigence 27.4)"""
        # Créer quelques notations
        Notation.objects.create(
            notateur=self.exploitant,
            note=self.agronome,
            note_valeur=5,
            commentaire='Excellent travail, très professionnel et compétent.',
            mission=self.mission,
            statut='PUBLIE'
        )
        
        self.client.force_authenticate(user=self.exploitant)
        
        # Filtrer par utilisateur noté
        response = self.client.get(f'/api/v1/ratings/?user_id={self.agronome.id}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_report_notation(self):
        """Test: Signaler une notation (Exigence 27.5)"""
        # Créer une notation
        notation = Notation.objects.create(
            notateur=self.exploitant,
            note=self.agronome,
            note_valeur=1,
            commentaire='Commentaire inapproprié pour test de signalement.',
            mission=self.mission,
            statut='PUBLIE'
        )
        
        # Se connecter en tant qu'agronome
        self.client.force_authenticate(user=self.agronome)
        
        data = {
            'motif': 'INAPPROPRIE',
            'description': 'Ce commentaire est offensant'
        }
        
        response = self.client.post(f'/api/v1/ratings/{notation.id}/report/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier que le signalement a été créé
        notation.refresh_from_db()
        self.assertEqual(notation.nombre_signalements, 1)


class QualityAlertTest(TestCase):
    """Tests pour les alertes qualité (Exigence 27.6)"""
    
    def setUp(self):
        """Configuration initiale"""
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
        
        self.agronome = User.objects.create_user(
            username='agronome@test.com',
            password='Test1234!',
            phone_number='+22890123457',
            user_type='AGRONOME'
        )
        from apps.users.models import AgronomeProfile
        AgronomeProfile.objects.create(
            user=self.agronome,
            canton_rattachement=self.canton,
            specialisations=['Maraîchage'],
            statut_validation='VALIDE',
            badge_valide=True
        )
    
    def test_quality_alert_triggered(self):
        """Test: Alerte qualité déclenchée (moyenne < 2.5 sur ≥ 10 avis)"""
        # Simuler 10 avis avec moyenne < 2.5
        alert = QualityAlertService.check_quality_alert(
            self.agronome,
            moyenne=2.3,
            nombre_avis=10
        )
        
        self.assertTrue(alert)
    
    def test_quality_alert_not_triggered_insufficient_reviews(self):
        """Test: Alerte non déclenchée si moins de 10 avis"""
        alert = QualityAlertService.check_quality_alert(
            self.agronome,
            moyenne=2.0,
            nombre_avis=5
        )
        
        self.assertFalse(alert)
    
    def test_quality_alert_not_triggered_good_rating(self):
        """Test: Alerte non déclenchée si moyenne ≥ 2.5"""
        alert = QualityAlertService.check_quality_alert(
            self.agronome,
            moyenne=3.0,
            nombre_avis=10
        )
        
        self.assertFalse(alert)
