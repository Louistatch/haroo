"""
Tests pour l'inscription des agronomes
Exigences: 7.1, 7.2, 7.3, 7.4
"""
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User, AgronomeProfile, DocumentJustificatif
from apps.locations.models import Region, Prefecture, Canton
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestAgronomeRegistration(TestCase):
    """Tests pour l'inscription des agronomes"""
    
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
        
        # URL de l'endpoint
        self.url = reverse('users:register-agronomist')
    
    def test_register_agronomist_success_without_documents(self):
        """
        Test d'inscription réussie d'un agronome sans documents
        Exigences: 7.1, 7.2, 7.3
        """
        data = {
            'username': 'agronome_test',
            'email': 'agronome@test.com',
            'phone_number': '+22890123456',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'canton_rattachement': self.canton.id,
            'specialisations': ['Cultures céréalières', 'Irrigation']
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Vérifier le statut de la réponse
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier que l'utilisateur a été créé
        self.assertTrue(User.objects.filter(username='agronome_test').exists())
        user = User.objects.get(username='agronome_test')
        
        # Vérifier le type d'utilisateur
        self.assertEqual(user.user_type, 'AGRONOME')
        
        # Vérifier que le profil agronome a été créé
        self.assertTrue(hasattr(user, 'agronome_profile'))
        profile = user.agronome_profile
        
        # Vérifier le statut EN_ATTENTE (Exigence 7.3)
        self.assertEqual(profile.statut_validation, 'EN_ATTENTE')
        self.assertFalse(profile.badge_valide)
        
        # Vérifier les spécialisations
        self.assertEqual(len(profile.specialisations), 2)
        self.assertIn('Cultures céréalières', profile.specialisations)
        self.assertIn('Irrigation', profile.specialisations)
        
        # Vérifier le canton
        self.assertEqual(profile.canton_rattachement.id, self.canton.id)
    
    def test_register_agronomist_with_documents(self):
        """
        Test d'inscription avec documents justificatifs
        Exigences: 7.4
        """
        # Créer un fichier PDF de test
        pdf_content = b'%PDF-1.4 fake pdf content'
        pdf_file = SimpleUploadedFile(
            "diplome.pdf",
            pdf_content,
            content_type="application/pdf"
        )
        
        data = {
            'username': 'agronome_docs',
            'email': 'agronome_docs@test.com',
            'phone_number': '+22890123457',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Marie',
            'last_name': 'Martin',
            'canton_rattachement': self.canton.id,
            'specialisations': ['Cultures maraîchères'],
            'documents': [pdf_file],
            'types_documents': ['DIPLOME']
        }
        
        response = self.client.post(self.url, data, format='multipart')
        
        # Vérifier le statut
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier que le document a été créé
        user = User.objects.get(username='agronome_docs')
        profile = user.agronome_profile
        
        documents = DocumentJustificatif.objects.filter(agronome_profile=profile)
        self.assertEqual(documents.count(), 1)
        
        doc = documents.first()
        self.assertEqual(doc.type_document, 'DIPLOME')
        self.assertEqual(doc.nom_fichier, 'diplome.pdf')
    
    def test_register_agronomist_missing_required_fields(self):
        """
        Test avec champs requis manquants
        Exigence: 7.1
        """
        data = {
            'username': 'agronome_incomplete',
            'email': 'incomplete@test.com',
            # Manque: phone_number, password, canton_rattachement, specialisations
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Doit échouer
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Vérifier que l'utilisateur n'a pas été créé
        self.assertFalse(User.objects.filter(username='agronome_incomplete').exists())
    
    def test_register_agronomist_invalid_specialisation(self):
        """
        Test avec spécialisation invalide
        Exigence: 7.2
        """
        data = {
            'username': 'agronome_invalid_spec',
            'email': 'invalid_spec@test.com',
            'phone_number': '+22890123458',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Paul',
            'last_name': 'Durand',
            'canton_rattachement': self.canton.id,
            'specialisations': ['Spécialisation Inexistante']
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Doit échouer
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('specialisations', response.data)
    
    def test_register_agronomist_empty_specialisations(self):
        """
        Test avec liste de spécialisations vide
        Exigence: 7.2
        """
        data = {
            'username': 'agronome_no_spec',
            'email': 'no_spec@test.com',
            'phone_number': '+22890123459',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Sophie',
            'last_name': 'Bernard',
            'canton_rattachement': self.canton.id,
            'specialisations': []
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Doit échouer
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_agronomist_invalid_canton(self):
        """
        Test avec canton invalide
        Exigence: 7.1
        """
        data = {
            'username': 'agronome_invalid_canton',
            'email': 'invalid_canton@test.com',
            'phone_number': '+22890123460',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Luc',
            'last_name': 'Petit',
            'canton_rattachement': 99999,  # Canton inexistant
            'specialisations': ['Cultures céréalières']
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Doit échouer
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_agronomist_duplicate_phone(self):
        """
        Test avec numéro de téléphone déjà utilisé
        """
        # Créer un premier utilisateur
        User.objects.create_user(
            username='existing_user',
            email='existing@test.com',
            phone_number='+22890123461',
            password='TestPass123!',
            user_type='AGRONOME'
        )
        
        # Essayer de créer un deuxième utilisateur avec le même numéro
        data = {
            'username': 'agronome_duplicate',
            'email': 'duplicate@test.com',
            'phone_number': '+22890123461',  # Même numéro
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'canton_rattachement': self.canton.id,
            'specialisations': ['Cultures céréalières']
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Doit échouer
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone_number', response.data)
    
    def test_register_agronomist_password_mismatch(self):
        """
        Test avec mots de passe non correspondants
        """
        data = {
            'username': 'agronome_pwd_mismatch',
            'email': 'pwd_mismatch@test.com',
            'phone_number': '+22890123462',
            'password': 'TestPass123!',
            'password_confirm': 'DifferentPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'canton_rattachement': self.canton.id,
            'specialisations': ['Cultures céréalières']
        }
        
        response = self.client.post(self.url, data, format='json')
        
        # Doit échouer
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)
