"""
Tests pour le système de vérification des exploitations
Exigences: 10.1, 10.2, 10.3, 10.4
"""
import os
import tempfile
from decimal import Decimal
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from apps.locations.models import Region, Prefecture, Canton
from .models import ExploitantProfile, FarmVerificationDocument
from .gps_validation import GPSValidationService

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class FarmVerificationTestCase(TestCase):
    """Tests pour la vérification des exploitations"""
    
    def setUp(self):
        """Configuration initiale des tests"""
        self.client = APIClient()
        
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
        
        # Créer un utilisateur exploitant
        self.exploitant = User.objects.create_user(
            username='exploitant_test',
            email='exploitant@test.com',
            phone_number='+22890123456',
            password='TestPass123!',
            user_type='EXPLOITANT',
            first_name='Jean',
            last_name='Dupont'
        )
        self.exploitant.phone_verified = True
        self.exploitant.save()
        
        # Créer un utilisateur non-exploitant
        self.non_exploitant = User.objects.create_user(
            username='acheteur_test',
            email='acheteur@test.com',
            phone_number='+22890123457',
            password='TestPass123!',
            user_type='ACHETEUR'
        )
        
        # Créer un fichier de test
        self.test_file = SimpleUploadedFile(
            "titre_foncier.pdf",
            b"file_content",
            content_type="application/pdf"
        )
    
    def test_gps_validation_minimum_superficie(self):
        """
        Test: Validation de la superficie minimale
        Exigence: 10.2
        """
        # Test avec superficie valide
        is_valid, error = GPSValidationService.validate_minimum_superficie(10.0)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Test avec superficie valide supérieure
        is_valid, error = GPSValidationService.validate_minimum_superficie(50.0)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Test avec superficie invalide
        is_valid, error = GPSValidationService.validate_minimum_superficie(5.0)
        self.assertFalse(is_valid)
        self.assertIn("10 hectares", error)
        
        # Test avec superficie limite
        is_valid, error = GPSValidationService.validate_minimum_superficie(9.99)
        self.assertFalse(is_valid)
    
    def test_gps_validation_coordinates_in_togo(self):
        """
        Test: Validation que les coordonnées sont au Togo
        Exigence: 10.4
        """
        # Coordonnées valides au Togo (Lomé)
        is_valid, error = GPSValidationService.validate_coordinates_in_togo(6.1319, 1.2228)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Coordonnées valides au Togo (Kara)
        is_valid, error = GPSValidationService.validate_coordinates_in_togo(9.5511, 1.1864)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Coordonnées invalides (hors Togo - latitude)
        is_valid, error = GPSValidationService.validate_coordinates_in_togo(5.0, 1.2)
        self.assertFalse(is_valid)
        self.assertIn("latitude", error.lower())
        
        # Coordonnées invalides (hors Togo - longitude)
        is_valid, error = GPSValidationService.validate_coordinates_in_togo(6.5, 3.0)
        self.assertFalse(is_valid)
        self.assertIn("longitude", error.lower())
    
    def test_gps_validation_area_estimation(self):
        """
        Test: Estimation de la superficie à partir de coordonnées GPS
        Exigence: 10.4
        """
        # Polygone carré approximatif de ~1 hectare (100m x 100m)
        # À 6° de latitude, 1 degré ≈ 111 km
        # Donc 100m ≈ 0.0009 degrés
        coordinates = [
            {'lat': 6.1319, 'lon': 1.2228},
            {'lat': 6.1328, 'lon': 1.2228},
            {'lat': 6.1328, 'lon': 1.2237},
            {'lat': 6.1319, 'lon': 1.2237},
        ]
        
        area = GPSValidationService.estimate_area_from_coordinates(coordinates)
        
        # L'aire devrait être proche de 1 hectare (avec tolérance)
        self.assertGreater(area, 0.5)
        self.assertLess(area, 2.0)
    
    def test_gps_validation_coherence_point_only(self):
        """
        Test: Validation avec un point GPS uniquement (pas de polygone)
        Exigence: 10.4
        """
        gps_coordinates = {
            'lat': 6.1319,
            'lon': 1.2228
        }
        
        is_valid, error, details = GPSValidationService.validate_gps_superficie_coherence(
            15.0,  # 15 hectares
            gps_coordinates
        )
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        self.assertEqual(details['validation_type'], 'point_only')
    
    def test_gps_validation_coherence_polygon(self):
        """
        Test: Validation de la cohérence GPS/superficie avec polygone
        Exigence: 10.4
        """
        # Polygone d'environ 10 hectares (316m x 316m)
        # 316m ≈ 0.00285 degrés à 6° de latitude
        coordinates = [
            {'lat': 6.1319, 'lon': 1.2228},
            {'lat': 6.1347, 'lon': 1.2228},
            {'lat': 6.1347, 'lon': 1.2256},
            {'lat': 6.1319, 'lon': 1.2256},
        ]
        
        gps_coordinates = {
            'type': 'polygon',
            'coordinates': coordinates
        }
        
        # Test avec superficie cohérente
        is_valid, error, details = GPSValidationService.validate_gps_superficie_coherence(
            10.0,
            gps_coordinates
        )
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        self.assertEqual(details['validation_type'], 'polygon')
        self.assertTrue(details['is_coherent'])
    
    def test_farm_verification_request_success(self):
        """
        Test: Demande de vérification réussie
        Exigences: 10.1, 10.2, 10.3, 10.4
        """
        self.client.force_authenticate(user=self.exploitant)
        
        # Créer un fichier de test
        test_file = SimpleUploadedFile(
            "titre_foncier.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        data = {
            'superficie_totale': '15.50',
            'canton_principal': self.canton.id,
            'coordonnees_gps': {
                'lat': 6.1319,
                'lon': 1.2228
            },
            'cultures_actuelles': ['Maïs', 'Soja'],
            'documents': [test_file],
            'types_documents': ['TITRE_FONCIER']
        }
        
        response = self.client.post(
            '/api/v1/farms/verification-request',
            data,
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('profile', response.data)
        
        # Vérifier que le profil a été créé
        profile = ExploitantProfile.objects.get(user=self.exploitant)
        self.assertEqual(profile.statut_verification, 'EN_ATTENTE')
        self.assertEqual(profile.superficie_totale, Decimal('15.50'))
        self.assertEqual(profile.canton_principal, self.canton)
        
        # Vérifier que le document a été uploadé
        self.assertEqual(
            FarmVerificationDocument.objects.filter(exploitant_profile=profile).count(),
            1
        )
    
    def test_farm_verification_request_insufficient_superficie(self):
        """
        Test: Rejet de demande avec superficie insuffisante
        Exigence: 10.2
        """
        self.client.force_authenticate(user=self.exploitant)
        
        test_file = SimpleUploadedFile(
            "titre_foncier.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        data = {
            'superficie_totale': '5.0',  # Moins de 10 hectares
            'canton_principal': self.canton.id,
            'coordonnees_gps': {
                'lat': 6.1319,
                'lon': 1.2228
            },
            'documents': [test_file],
            'types_documents': ['TITRE_FONCIER']
        }
        
        response = self.client.post(
            '/api/v1/farms/verification-request',
            data,
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('superficie_totale', response.data['details'])
    
    def test_farm_verification_request_invalid_coordinates(self):
        """
        Test: Rejet de demande avec coordonnées GPS invalides
        Exigence: 10.4
        """
        self.client.force_authenticate(user=self.exploitant)
        
        test_file = SimpleUploadedFile(
            "titre_foncier.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        data = {
            'superficie_totale': '15.0',
            'canton_principal': self.canton.id,
            'coordonnees_gps': {
                'lat': 5.0,  # Hors Togo
                'lon': 1.2
            },
            'documents': [test_file],
            'types_documents': ['TITRE_FONCIER']
        }
        
        response = self.client.post(
            '/api/v1/farms/verification-request',
            data,
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_farm_verification_request_no_documents(self):
        """
        Test: Rejet de demande sans documents justificatifs
        Exigence: 10.3
        """
        self.client.force_authenticate(user=self.exploitant)
        
        data = {
            'superficie_totale': '15.0',
            'canton_principal': self.canton.id,
            'coordonnees_gps': {
                'lat': 6.1319,
                'lon': 1.2228
            },
            'documents': [],
            'types_documents': []
        }
        
        response = self.client.post(
            '/api/v1/farms/verification-request',
            data,
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_farm_verification_request_non_exploitant(self):
        """
        Test: Rejet de demande pour un non-exploitant
        Exigence: 10.1
        """
        self.client.force_authenticate(user=self.non_exploitant)
        
        test_file = SimpleUploadedFile(
            "titre_foncier.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        data = {
            'superficie_totale': '15.0',
            'canton_principal': self.canton.id,
            'coordonnees_gps': {
                'lat': 6.1319,
                'lon': 1.2228
            },
            'documents': [test_file],
            'types_documents': ['TITRE_FONCIER']
        }
        
        response = self.client.post(
            '/api/v1/farms/verification-request',
            data,
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['code'], 'NOT_EXPLOITANT')
    
    def test_farm_verification_status(self):
        """
        Test: Récupération du statut de vérification
        Exigence: 10.4, 10.5
        """
        # Créer un profil exploitant
        profile = ExploitantProfile.objects.create(
            user=self.exploitant,
            superficie_totale=Decimal('15.0'),
            canton_principal=self.canton,
            coordonnees_gps={'lat': 6.1319, 'lon': 1.2228},
            statut_verification='EN_ATTENTE'
        )
        
        self.client.force_authenticate(user=self.exploitant)
        
        response = self.client.get('/api/v1/farms/verification-status')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['statut_verification'], 'EN_ATTENTE')
        self.assertEqual(response.data['superficie_totale'], '15.00')
    
    def test_farm_premium_features_verified(self):
        """
        Test: Fonctionnalités premium pour exploitant vérifié
        Exigence: 10.5, 10.6
        """
        # Créer un profil exploitant vérifié
        profile = ExploitantProfile.objects.create(
            user=self.exploitant,
            superficie_totale=Decimal('15.0'),
            canton_principal=self.canton,
            coordonnees_gps={'lat': 6.1319, 'lon': 1.2228},
            statut_verification='VERIFIE'
        )
        
        self.client.force_authenticate(user=self.exploitant)
        
        response = self.client.get('/api/v1/farms/me/premium-features')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_verified'])
        self.assertEqual(response.data['statut_verification'], 'VERIFIE')
        
        # Vérifier que toutes les fonctionnalités sont activées
        features = response.data['features']
        for feature_name, feature_data in features.items():
            self.assertTrue(feature_data['enabled'], f"Feature {feature_name} should be enabled")
    
    def test_farm_premium_features_not_verified(self):
        """
        Test: Fonctionnalités premium pour exploitant non vérifié
        Exigence: 10.5, 10.6
        """
        # Créer un profil exploitant non vérifié
        profile = ExploitantProfile.objects.create(
            user=self.exploitant,
            superficie_totale=Decimal('15.0'),
            canton_principal=self.canton,
            coordonnees_gps={'lat': 6.1319, 'lon': 1.2228},
            statut_verification='EN_ATTENTE'
        )
        
        self.client.force_authenticate(user=self.exploitant)
        
        response = self.client.get('/api/v1/farms/me/premium-features')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_verified'])
        self.assertIn('message', response.data)
        
        # Vérifier que toutes les fonctionnalités sont désactivées
        features = response.data['features']
        for feature_name, feature_data in features.items():
            self.assertFalse(feature_data['enabled'], f"Feature {feature_name} should be disabled")
    
    def test_calculate_distance(self):
        """
        Test: Calcul de distance entre deux points GPS
        """
        # Distance entre Lomé et Kara (environ 400 km)
        distance = GPSValidationService.calculate_distance_km(
            6.1319, 1.2228,  # Lomé
            9.5511, 1.1864   # Kara
        )
        
        # La distance devrait être d'environ 380-420 km
        self.assertGreater(distance, 350)
        self.assertLess(distance, 450)
