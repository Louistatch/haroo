"""
Tests pour les modèles de profils utilisateurs
Exigences: 2.1, 2.5
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from apps.users.models import (
    User,
    ExploitantProfile,
    AgronomeProfile,
    OuvrierProfile,
    AcheteurProfile,
    InstitutionProfile
)
from apps.locations.models import Region, Prefecture, Canton


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
def exploitant_user(db):
    """Créer un utilisateur exploitant"""
    return User.objects.create_user(
        username="exploitant_test",
        email="exploitant@test.com",
        phone_number="+22890123456",
        user_type="EXPLOITANT",
        password="testpass123"
    )


@pytest.fixture
def agronome_user(db):
    """Créer un utilisateur agronome"""
    return User.objects.create_user(
        username="agronome_test",
        email="agronome@test.com",
        phone_number="+22890123457",
        user_type="AGRONOME",
        password="testpass123"
    )


@pytest.fixture
def ouvrier_user(db):
    """Créer un utilisateur ouvrier"""
    return User.objects.create_user(
        username="ouvrier_test",
        email="ouvrier@test.com",
        phone_number="+22890123458",
        user_type="OUVRIER",
        password="testpass123"
    )


@pytest.fixture
def acheteur_user(db):
    """Créer un utilisateur acheteur"""
    return User.objects.create_user(
        username="acheteur_test",
        email="acheteur@test.com",
        phone_number="+22890123459",
        user_type="ACHETEUR",
        password="testpass123"
    )


@pytest.fixture
def institution_user(db):
    """Créer un utilisateur institution"""
    return User.objects.create_user(
        username="institution_test",
        email="institution@test.com",
        phone_number="+22890123460",
        user_type="INSTITUTION",
        password="testpass123"
    )


@pytest.mark.django_db
class TestExploitantProfile:
    """Tests pour le modèle ExploitantProfile"""
    
    def test_create_exploitant_profile(self, exploitant_user, canton):
        """Test de création d'un profil exploitant"""
        profile = ExploitantProfile.objects.create(
            user=exploitant_user,
            superficie_totale=Decimal("15.50"),
            canton_principal=canton,
            coordonnees_gps={"lat": 6.1319, "lon": 1.2228},
            cultures_actuelles=["Maïs", "Tomate"]
        )
        
        assert profile.user == exploitant_user
        assert profile.superficie_totale == Decimal("15.50")
        assert profile.canton_principal == canton
        assert profile.statut_verification == "NON_VERIFIE"
        assert profile.cultures_actuelles == ["Maïs", "Tomate"]
    
    def test_exploitant_profile_validation_superficie_positive(self, exploitant_user, canton):
        """Test que la superficie doit être positive"""
        profile = ExploitantProfile(
            user=exploitant_user,
            superficie_totale=Decimal("-5.00"),
            canton_principal=canton,
            coordonnees_gps={"lat": 6.1319, "lon": 1.2228}
        )
        
        with pytest.raises(ValidationError):
            profile.clean()
    
    def test_exploitant_profile_statut_choices(self, exploitant_user, canton):
        """Test des différents statuts de vérification"""
        profile = ExploitantProfile.objects.create(
            user=exploitant_user,
            superficie_totale=Decimal("20.00"),
            canton_principal=canton,
            coordonnees_gps={"lat": 6.1319, "lon": 1.2228}
        )
        
        # Test des différents statuts
        for statut, _ in ExploitantProfile.STATUT_VERIFICATION_CHOICES:
            profile.statut_verification = statut
            profile.save()
            assert profile.statut_verification == statut


@pytest.mark.django_db
class TestAgronomeProfile:
    """Tests pour le modèle AgronomeProfile"""
    
    def test_create_agronome_profile(self, agronome_user, canton):
        """Test de création d'un profil agronome"""
        profile = AgronomeProfile.objects.create(
            user=agronome_user,
            canton_rattachement=canton,
            specialisations=["Maraîchage", "Irrigation"]
        )
        
        assert profile.user == agronome_user
        assert profile.canton_rattachement == canton
        assert profile.statut_validation == "EN_ATTENTE"
        assert profile.badge_valide is False
        assert profile.note_moyenne == Decimal("0.00")
        assert profile.nombre_avis == 0
    
    def test_agronome_profile_validation_status(self, agronome_user, canton):
        """Test des différents statuts de validation"""
        profile = AgronomeProfile.objects.create(
            user=agronome_user,
            canton_rattachement=canton,
            specialisations=["Cultures céréalières"]
        )
        
        # Test validation
        profile.statut_validation = "VALIDE"
        profile.badge_valide = True
        profile.save()
        
        assert profile.statut_validation == "VALIDE"
        assert profile.badge_valide is True


@pytest.mark.django_db
class TestOuvrierProfile:
    """Tests pour le modèle OuvrierProfile"""
    
    def test_create_ouvrier_profile(self, ouvrier_user, canton):
        """Test de création d'un profil ouvrier"""
        profile = OuvrierProfile.objects.create(
            user=ouvrier_user,
            competences=["Récolte", "Plantation", "Irrigation"]
        )
        profile.cantons_disponibles.add(canton)
        
        assert profile.user == ouvrier_user
        assert profile.competences == ["Récolte", "Plantation", "Irrigation"]
        assert profile.disponible is True
        assert profile.note_moyenne == Decimal("0.00")
        assert canton in profile.cantons_disponibles.all()
    
    def test_ouvrier_profile_disponibilite(self, ouvrier_user):
        """Test de la disponibilité de l'ouvrier"""
        profile = OuvrierProfile.objects.create(
            user=ouvrier_user,
            competences=["Récolte"],
            disponible=False
        )
        
        assert profile.disponible is False


@pytest.mark.django_db
class TestAcheteurProfile:
    """Tests pour le modèle AcheteurProfile"""
    
    def test_create_acheteur_profile(self, acheteur_user):
        """Test de création d'un profil acheteur"""
        profile = AcheteurProfile.objects.create(
            user=acheteur_user,
            type_acheteur="ENTREPRISE",
            volume_achats_annuel=Decimal("500.00")
        )
        
        assert profile.user == acheteur_user
        assert profile.type_acheteur == "ENTREPRISE"
        assert profile.volume_achats_annuel == Decimal("500.00")
    
    def test_acheteur_profile_types(self, acheteur_user):
        """Test des différents types d'acheteurs"""
        profile = AcheteurProfile.objects.create(
            user=acheteur_user,
            type_acheteur="PARTICULIER"
        )
        
        # Test des différents types
        for type_acheteur, _ in AcheteurProfile.TYPE_ACHETEUR_CHOICES:
            profile.type_acheteur = type_acheteur
            profile.save()
            assert profile.type_acheteur == type_acheteur


@pytest.mark.django_db
class TestInstitutionProfile:
    """Tests pour le modèle InstitutionProfile"""
    
    def test_create_institution_profile(self, institution_user, region):
        """Test de création d'un profil institution"""
        profile = InstitutionProfile.objects.create(
            user=institution_user,
            nom_organisme="Ministère de l'Agriculture",
            niveau_acces="NATIONAL"
        )
        profile.regions_acces.add(region)
        
        assert profile.user == institution_user
        assert profile.nom_organisme == "Ministère de l'Agriculture"
        assert profile.niveau_acces == "NATIONAL"
        assert region in profile.regions_acces.all()
    
    def test_institution_profile_niveaux_acces(self, institution_user):
        """Test des différents niveaux d'accès"""
        profile = InstitutionProfile.objects.create(
            user=institution_user,
            nom_organisme="Direction Régionale",
            niveau_acces="REGIONAL"
        )
        
        # Test des différents niveaux
        for niveau, _ in InstitutionProfile.NIVEAU_ACCES_CHOICES:
            profile.niveau_acces = niveau
            profile.save()
            assert profile.niveau_acces == niveau
