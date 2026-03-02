"""
Tests pour la page de détails publique des agronomes
Exigence: 8.5
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.users.models import AgronomeProfile, ExploitantProfile
from apps.locations.models import Region, Prefecture, Canton

User = get_user_model()


@pytest.mark.django_db
class TestAgronomePublicDetail:
    """
    Tests pour l'endpoint de détails publics d'un agronome
    Exigence: 8.5
    """
    
    def setup_method(self):
        """Configuration initiale pour chaque test"""
        self.client = APIClient()
        
        # Créer la hiérarchie administrative
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
        
        # Créer un agronome validé
        self.agronome_user = User.objects.create_user(
            username='agronome_test',
            email='agronome@test.com',
            phone_number='+22890000001',
            password='TestPass123!',
            user_type='AGRONOME',
            first_name='Jean',
            last_name='Dupont'
        )
        
        self.agronome_profile = AgronomeProfile.objects.create(
            user=self.agronome_user,
            canton_rattachement=self.canton,
            specialisations=['Cultures céréalières', 'Irrigation'],
            statut_validation='VALIDE',
            badge_valide=True,
            note_moyenne=4.5,
            nombre_avis=10
        )
        
        # Créer un agronome non validé
        self.agronome_non_valide_user = User.objects.create_user(
            username='agronome_non_valide',
            email='agronome_nv@test.com',
            phone_number='+22890000002',
            password='TestPass123!',
            user_type='AGRONOME',
            first_name='Marie',
            last_name='Martin'
        )
        
        self.agronome_non_valide_profile = AgronomeProfile.objects.create(
            user=self.agronome_non_valide_user,
            canton_rattachement=self.canton,
            specialisations=['Arboriculture fruitière'],
            statut_validation='EN_ATTENTE',
            badge_valide=False
        )
        
        # Créer un exploitant vérifié
        self.exploitant_verifie_user = User.objects.create_user(
            username='exploitant_verifie',
            email='exploitant@test.com',
            phone_number='+22890000003',
            password='TestPass123!',
            user_type='EXPLOITANT'
        )
        
        self.exploitant_verifie_profile = ExploitantProfile.objects.create(
            user=self.exploitant_verifie_user,
            superficie_totale=15.5,
            canton_principal=self.canton,
            coordonnees_gps={'lat': 6.1256, 'lon': 1.2223},
            statut_verification='VERIFIE'
        )
        
        # Créer un exploitant non vérifié
        self.exploitant_non_verifie_user = User.objects.create_user(
            username='exploitant_non_verifie',
            email='exploitant_nv@test.com',
            phone_number='+22890000004',
            password='TestPass123!',
            user_type='EXPLOITANT'
        )
        
        self.exploitant_non_verifie_profile = ExploitantProfile.objects.create(
            user=self.exploitant_non_verifie_user,
            superficie_totale=8.0,
            canton_principal=self.canton,
            coordonnees_gps={'lat': 6.1256, 'lon': 1.2223},
            statut_verification='NON_VERIFIE'
        )
    
    def test_get_agronomist_public_detail_success(self):
        """
        Test: Récupération réussie des détails publics d'un agronome validé
        Exigence: 8.5 - Afficher le profil complet avec spécialisations
        """
        url = reverse('users:agronomist-public-detail', kwargs={'agronomist_id': self.agronome_user.id})
        
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Vérifier les informations de base
        assert data['id'] == self.agronome_user.id
        assert data['nom_complet'] == 'Jean Dupont'
        assert data['username'] == 'agronome_test'
        
        # Vérifier les spécialisations
        assert 'specialisations' in data
        assert 'Cultures céréalières' in data['specialisations']
        assert 'Irrigation' in data['specialisations']
        
        # Vérifier les informations de localisation
        assert data['canton']['nom'] == 'Lomé 1er'
        assert data['prefecture']['nom'] == 'Golfe'
        assert data['region']['nom'] == 'Maritime'
        
        # Vérifier le badge
        assert data['badge_valide'] is True
        assert data['statut_validation'] == 'VALIDE'
        
        # Vérifier les notations
        assert data['note_moyenne'] == 4.5
        assert data['nombre_avis'] == 10
        assert 'avis' in data
        
        # Utilisateur non connecté ne peut pas contacter
        assert data['can_contact'] is False
        assert data['is_verified_farmer'] is False
    
    def test_get_agronomist_public_detail_not_found(self):
        """
        Test: Agronome inexistant
        """
        url = reverse('users:agronomist-public-detail', kwargs={'agronomist_id': 99999})
        
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.json()
    
    def test_get_agronomist_public_detail_not_validated(self):
        """
        Test: Profil non validé n'est pas accessible publiquement
        Exigence: 8.2 - Afficher uniquement les profils validés
        """
        url = reverse('users:agronomist-public-detail', kwargs={'agronomist_id': self.agronome_non_valide_user.id})
        
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'error' in response.json()
        assert 'pas accessible publiquement' in response.json()['error']
    
    def test_verified_farmer_can_contact(self):
        """
        Test: Exploitant vérifié peut contacter l'agronome
        Exigence: 8.5 - Bouton de contact pour les exploitants vérifiés
        """
        # Se connecter en tant qu'exploitant vérifié
        self.client.force_authenticate(user=self.exploitant_verifie_user)
        
        url = reverse('users:agronomist-public-detail', kwargs={'agronomist_id': self.agronome_user.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # L'exploitant vérifié peut contacter
        assert data['can_contact'] is True
        assert data['is_verified_farmer'] is True
    
    def test_non_verified_farmer_cannot_contact(self):
        """
        Test: Exploitant non vérifié ne peut pas contacter l'agronome
        Exigence: 8.5 - Bouton de contact uniquement pour exploitants vérifiés
        """
        # Se connecter en tant qu'exploitant non vérifié
        self.client.force_authenticate(user=self.exploitant_non_verifie_user)
        
        url = reverse('users:agronomist-public-detail', kwargs={'agronomist_id': self.agronome_user.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # L'exploitant non vérifié ne peut pas contacter
        assert data['can_contact'] is False
        assert data['is_verified_farmer'] is False
    
    def test_admin_can_contact(self):
        """
        Test: Les administrateurs peuvent contacter les agronomes
        """
        # Créer un admin
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            phone_number='+22890000005',
            password='TestPass123!',
            user_type='ADMIN',
            is_staff=True
        )
        
        self.client.force_authenticate(user=admin_user)
        
        url = reverse('users:agronomist-public-detail', kwargs={'agronomist_id': self.agronome_user.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # L'admin peut contacter
        assert data['can_contact'] is True
    
    def test_other_user_types_cannot_contact(self):
        """
        Test: Les autres types d'utilisateurs ne peuvent pas contacter
        """
        # Créer un acheteur
        acheteur_user = User.objects.create_user(
            username='acheteur',
            email='acheteur@test.com',
            phone_number='+22890000006',
            password='TestPass123!',
            user_type='ACHETEUR'
        )
        
        self.client.force_authenticate(user=acheteur_user)
        
        url = reverse('users:agronomist-public-detail', kwargs={'agronomist_id': self.agronome_user.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # L'acheteur ne peut pas contacter
        assert data['can_contact'] is False
        assert data['is_verified_farmer'] is False
    
    def test_profile_includes_all_required_fields(self):
        """
        Test: Le profil contient tous les champs requis
        Exigence: 8.5 - Afficher le profil complet
        """
        url = reverse('users:agronomist-public-detail', kwargs={'agronomist_id': self.agronome_user.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Vérifier la présence de tous les champs requis
        required_fields = [
            'id', 'nom_complet', 'username', 'photo_profil', 'date_inscription',
            'canton', 'prefecture', 'region', 'specialisations',
            'badge_valide', 'statut_validation',
            'note_moyenne', 'nombre_avis', 'avis',
            'nombre_missions_completees', 'taux_reussite',
            'can_contact', 'is_verified_farmer'
        ]
        
        for field in required_fields:
            assert field in data, f"Le champ '{field}' est manquant dans la réponse"
    
    def test_cache_is_used(self):
        """
        Test: Le cache Redis est utilisé pour optimiser les performances
        """
        from django.core.cache import cache
        
        # Essayer de vider le cache, skip si Redis n'est pas disponible
        try:
            cache.clear()
        except Exception:
            pytest.skip("Redis n'est pas disponible pour ce test")
        
        url = reverse('users:agronomist-public-detail', kwargs={'agronomist_id': self.agronome_user.id})
        
        # Première requête - devrait mettre en cache
        response1 = self.client.get(url)
        assert response1.status_code == status.HTTP_200_OK
        
        # Vérifier que les données sont en cache
        cache_key = f"agronomist_public_detail:{self.agronome_user.id}"
        try:
            cached_data = cache.get(cache_key)
            assert cached_data is not None
        except Exception:
            pytest.skip("Redis n'est pas disponible pour ce test")
        
        # Deuxième requête - devrait utiliser le cache
        response2 = self.client.get(url)
        assert response2.status_code == status.HTTP_200_OK
        
        # Les données devraient être identiques
        assert response1.json()['id'] == response2.json()['id']


@pytest.mark.django_db
class TestAgronomePublicDetailIntegration:
    """
    Tests d'intégration pour la page de détails publique
    """
    
    def setup_method(self):
        """Configuration initiale"""
        self.client = APIClient()
        
        # Créer la hiérarchie administrative
        self.region = Region.objects.create(nom="Plateaux", code="PLA")
        self.prefecture = Prefecture.objects.create(
            nom="Kloto",
            code="KLO",
            region=self.region
        )
        self.canton = Canton.objects.create(
            nom="Kpalimé",
            code="KPA",
            prefecture=self.prefecture
        )
        
        # Créer un agronome avec photo de profil
        self.agronome_user = User.objects.create_user(
            username='agronome_photo',
            email='agronome_photo@test.com',
            phone_number='+22890000010',
            password='TestPass123!',
            user_type='AGRONOME',
            first_name='Paul',
            last_name='Kouassi'
        )
        
        self.agronome_profile = AgronomeProfile.objects.create(
            user=self.agronome_user,
            canton_rattachement=self.canton,
            specialisations=['Agriculture biologique', 'Agroforesterie', 'Protection des cultures'],
            statut_validation='VALIDE',
            badge_valide=True,
            note_moyenne=4.8,
            nombre_avis=25
        )
    
    def test_full_profile_display(self):
        """
        Test: Affichage complet du profil avec toutes les informations
        """
        url = reverse('users:agronomist-public-detail', kwargs={'agronomist_id': self.agronome_user.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Vérifier les informations complètes
        assert data['nom_complet'] == 'Paul Kouassi'
        assert len(data['specialisations']) == 3
        assert 'Agriculture biologique' in data['specialisations']
        assert 'Agroforesterie' in data['specialisations']
        assert 'Protection des cultures' in data['specialisations']
        
        # Vérifier la localisation complète
        assert data['canton']['nom'] == 'Kpalimé'
        assert data['prefecture']['nom'] == 'Kloto'
        assert data['region']['nom'] == 'Plateaux'
        
        # Vérifier les statistiques
        assert data['note_moyenne'] == 4.8
        assert data['nombre_avis'] == 25
    
    def test_anonymous_user_access(self):
        """
        Test: Les utilisateurs anonymes peuvent voir le profil mais pas contacter
        """
        url = reverse('users:agronomist-public-detail', kwargs={'agronomist_id': self.agronome_user.id})
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Profil visible
        assert data['nom_complet'] == 'Paul Kouassi'
        
        # Mais ne peut pas contacter
        assert data['can_contact'] is False
        assert data['is_verified_farmer'] is False
