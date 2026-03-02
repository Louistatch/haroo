"""
Tests pour les endpoints de gestion de profil
Exigences: 2.5, 31.1, 31.3
"""
import pytest
import io
from decimal import Decimal
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from apps.users.models import User, ExploitantProfile, AgronomeProfile
from apps.locations.models import Region, Prefecture, Canton


@pytest.fixture
def api_client():
    """Client API pour les tests"""
    return APIClient()


@pytest.fixture
def region(db):
    """Créer une région de test"""
    return Region.objects.create(nom="Maritime", code="MAR")


@pytest.fixture
def prefecture(db, region):
    """Créer une préfecture de test"""
    return Prefecture.objects.create(
        nom="Golfe",
        code="GOL",
        region=region
    )


@pytest.fixture
def canton(db, prefecture):
    """Créer un canton de test"""
    return Canton.objects.create(
        nom="Lomé 1er",
        code="LOM1",
        prefecture=prefecture,
        coordonnees_centre={"lat": 6.1319, "lon": 1.2228}
    )


@pytest.fixture
def exploitant_user_with_profile(db, canton):
    """Créer un utilisateur exploitant avec profil"""
    user = User.objects.create_user(
        username="exploitant_test",
        email="exploitant@test.com",
        phone_number="+22890123456",
        user_type="EXPLOITANT",
        password="testpass123",
        first_name="Jean",
        last_name="Dupont"
    )
    ExploitantProfile.objects.create(
        user=user,
        superficie_totale=Decimal("15.50"),
        canton_principal=canton,
        coordonnees_gps={"lat": 6.1319, "lon": 1.2228},
        cultures_actuelles=["Maïs", "Tomate"]
    )
    return user


@pytest.fixture
def agronome_user_with_profile(db, canton):
    """Créer un utilisateur agronome avec profil"""
    user = User.objects.create_user(
        username="agronome_test",
        email="agronome@test.com",
        phone_number="+22890123457",
        user_type="AGRONOME",
        password="testpass123",
        first_name="Marie",
        last_name="Martin"
    )
    AgronomeProfile.objects.create(
        user=user,
        canton_rattachement=canton,
        specialisations=["Maraîchage", "Irrigation"]
    )
    return user


def create_test_image():
    """Créer une image de test"""
    file = io.BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'JPEG')
    file.seek(0)
    return SimpleUploadedFile(
        "test_image.jpg",
        file.read(),
        content_type="image/jpeg"
    )


def create_large_image():
    """Créer une image trop grande (> 5 Mo)"""
    file = io.BytesIO()
    # Créer une très grande image pour dépasser 5 Mo
    image = Image.new('RGB', (8000, 8000), color='blue')
    image.save(file, 'JPEG', quality=95)
    file.seek(0)
    content = file.read()
    
    # S'assurer que le fichier est vraiment > 5 Mo
    if len(content) < 5 * 1024 * 1024:
        # Si pas assez grand, dupliquer le contenu
        content = content * 3
    
    return SimpleUploadedFile(
        "large_image.jpg",
        content,
        content_type="image/jpeg"
    )


@pytest.mark.django_db
class TestGetCurrentUserEndpoint:
    """Tests pour GET /api/v1/users/me"""
    
    def test_get_current_user_authenticated(self, api_client, exploitant_user_with_profile):
        """Test récupération du profil utilisateur authentifié"""
        # Authentifier l'utilisateur
        api_client.force_authenticate(user=exploitant_user_with_profile)
        
        # Faire la requête
        response = api_client.get('/api/v1/users/me')
        
        # Vérifications
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'exploitant_test'
        assert response.data['email'] == 'exploitant@test.com'
        assert response.data['user_type'] == 'EXPLOITANT'
        assert response.data['first_name'] == 'Jean'
        assert response.data['last_name'] == 'Dupont'
        
        # Vérifier que le profil exploitant est inclus
        assert 'exploitant_profile' in response.data
        assert response.data['exploitant_profile']['superficie_totale'] == '15.50'
        assert response.data['exploitant_profile']['cultures_actuelles'] == ['Maïs', 'Tomate']
    
    def test_get_current_user_unauthenticated(self, api_client):
        """Test que l'endpoint nécessite une authentification"""
        response = api_client.get('/api/v1/users/me')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_agronome(self, api_client, agronome_user_with_profile):
        """Test récupération du profil agronome"""
        api_client.force_authenticate(user=agronome_user_with_profile)
        
        response = api_client.get('/api/v1/users/me')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user_type'] == 'AGRONOME'
        assert 'agronome_profile' in response.data
        assert response.data['agronome_profile']['specialisations'] == ['Maraîchage', 'Irrigation']


@pytest.mark.django_db
class TestUpdateProfileEndpoint:
    """Tests pour PATCH /api/v1/users/me"""
    
    def test_update_basic_user_info(self, api_client, exploitant_user_with_profile):
        """Test mise à jour des informations de base"""
        api_client.force_authenticate(user=exploitant_user_with_profile)
        
        data = {
            'first_name': 'Jean-Pierre',
            'last_name': 'Durand',
            'email': 'jeanpierre@test.com'
        }
        
        response = api_client.patch('/api/v1/users/me', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['first_name'] == 'Jean-Pierre'
        assert response.data['user']['last_name'] == 'Durand'
        assert response.data['user']['email'] == 'jeanpierre@test.com'
        
        # Vérifier en base de données
        exploitant_user_with_profile.refresh_from_db()
        assert exploitant_user_with_profile.first_name == 'Jean-Pierre'
    
    def test_update_exploitant_profile(self, api_client, exploitant_user_with_profile, canton):
        """Test mise à jour du profil exploitant"""
        api_client.force_authenticate(user=exploitant_user_with_profile)
        
        data = {
            'exploitant_profile': {
                'cultures_actuelles': ['Maïs', 'Tomate', 'Piment']
            }
        }
        
        response = api_client.patch('/api/v1/users/me', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'Piment' in response.data['user']['exploitant_profile']['cultures_actuelles']
        
        # Vérifier en base de données
        profile = exploitant_user_with_profile.exploitant_profile
        profile.refresh_from_db()
        assert 'Piment' in profile.cultures_actuelles
    
    def test_update_agronome_profile(self, api_client, agronome_user_with_profile):
        """Test mise à jour du profil agronome"""
        api_client.force_authenticate(user=agronome_user_with_profile)
        
        data = {
            'agronome_profile': {
                'specialisations': ['Maraîchage', 'Irrigation', 'Cultures céréalières']
            }
        }
        
        response = api_client.patch('/api/v1/users/me', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['user']['agronome_profile']['specialisations']) == 3
    
    def test_cannot_update_readonly_fields(self, api_client, exploitant_user_with_profile):
        """Test que les champs en lecture seule ne peuvent pas être modifiés"""
        api_client.force_authenticate(user=exploitant_user_with_profile)
        
        data = {
            'phone_verified': True,
            'two_factor_enabled': True
        }
        
        response = api_client.patch('/api/v1/users/me', data, format='json')
        
        # La requête devrait réussir mais les champs ne doivent pas être modifiés
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['phone_verified'] is False
        assert response.data['user']['two_factor_enabled'] is False
    
    def test_update_profile_unauthenticated(self, api_client):
        """Test que l'endpoint nécessite une authentification"""
        data = {'first_name': 'Test'}
        response = api_client.patch('/api/v1/users/me', data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPhotoProfilUpload:
    """Tests pour l'upload de photo de profil - Exigences: 31.1, 31.3"""
    
    def test_upload_valid_photo(self, api_client, exploitant_user_with_profile):
        """Test upload d'une photo valide"""
        api_client.force_authenticate(user=exploitant_user_with_profile)
        
        photo = create_test_image()
        data = {'photo_profil': photo}
        
        response = api_client.patch('/api/v1/users/me', data, format='multipart')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['photo_profil'] is not None
        
        # Vérifier en base de données
        exploitant_user_with_profile.refresh_from_db()
        assert exploitant_user_with_profile.photo_profil is not None
    
    def test_upload_photo_too_large(self, api_client, exploitant_user_with_profile):
        """Test upload d'une photo trop grande (> 5 Mo) - Exigence: 31.2
        
        Note: Ce test vérifie que la validation de taille fonctionne.
        En pratique, créer une image JPEG > 5Mo est difficile car la compression
        est très efficace. Le test vérifie que la logique de validation existe.
        """
        api_client.force_authenticate(user=exploitant_user_with_profile)
        
        # Créer un fichier factice qui dépasse la limite
        # (simuler un fichier trop grand sans créer réellement une énorme image)
        large_content = b'0' * (6 * 1024 * 1024)  # 6 Mo de données
        
        large_photo = SimpleUploadedFile(
            "large_image.jpg",
            large_content,
            content_type="image/jpeg"
        )
        
        data = {'photo_profil': large_photo}
        
        response = api_client.patch('/api/v1/users/me', data, format='multipart')
        
        # Devrait échouer avec une erreur de validation
        # (soit au niveau de la validation du serializer, soit au niveau Django)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_upload_invalid_file_type(self, api_client, exploitant_user_with_profile):
        """Test upload d'un fichier non-image - Exigence: 31.1"""
        api_client.force_authenticate(user=exploitant_user_with_profile)
        
        # Créer un fichier texte
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"This is not an image",
            content_type="text/plain"
        )
        data = {'photo_profil': invalid_file}
        
        response = api_client.patch('/api/v1/users/me', data, format='multipart')
        
        # Devrait échouer avec une erreur de validation
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'photo_profil' in response.data
    
    def test_remove_photo(self, api_client, exploitant_user_with_profile):
        """Test suppression de la photo de profil"""
        # D'abord ajouter une photo
        exploitant_user_with_profile.photo_profil = create_test_image()
        exploitant_user_with_profile.save()
        
        api_client.force_authenticate(user=exploitant_user_with_profile)
        
        # Envoyer null pour supprimer la photo
        data = {'photo_profil': None}
        response = api_client.patch('/api/v1/users/me', data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier en base de données
        exploitant_user_with_profile.refresh_from_db()
        assert not exploitant_user_with_profile.photo_profil


@pytest.mark.django_db
class TestProfileValidation:
    """Tests de validation des données de profil - Exigence: 2.5"""
    
    def test_validate_exploitant_superficie(self, api_client, exploitant_user_with_profile):
        """Test validation de la superficie pour exploitant"""
        api_client.force_authenticate(user=exploitant_user_with_profile)
        
        # Essayer de mettre une superficie négative
        data = {
            'exploitant_profile': {
                'superficie_totale': '-10.00'
            }
        }
        
        response = api_client.patch('/api/v1/users/me', data, format='json')
        
        # Devrait échouer avec une erreur de validation
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_validate_email_format(self, api_client, exploitant_user_with_profile):
        """Test validation du format email"""
        api_client.force_authenticate(user=exploitant_user_with_profile)
        
        data = {'email': 'invalid-email'}
        response = api_client.patch('/api/v1/users/me', data, format='json')
        
        # Devrait échouer avec une erreur de validation
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
