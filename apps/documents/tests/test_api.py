"""
Tests pour les endpoints API des documents techniques
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.cache import cache
from decimal import Decimal

from apps.documents.models import DocumentTechnique, DocumentTemplate
from apps.locations.models import Region, Prefecture, Canton
from apps.users.models import User


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Configure le cache pour les tests"""
    pass


@pytest.fixture(autouse=True)
def use_dummy_cache(settings):
    """Utilise le cache en mémoire pour tous les tests"""
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }


@pytest.fixture
def api_client():
    """Client API pour les tests"""
    return APIClient()


@pytest.fixture
def clear_cache():
    """Nettoie le cache avant chaque test"""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def region():
    """Crée une région de test"""
    return Region.objects.create(nom="Maritime", code="MAR")


@pytest.fixture
def prefecture(region):
    """Crée une préfecture de test"""
    return Prefecture.objects.create(
        nom="Golfe",
        code="GOL",
        region=region
    )


@pytest.fixture
def canton(prefecture):
    """Crée un canton de test"""
    return Canton.objects.create(
        nom="Lomé 1er",
        code="LOM1",
        prefecture=prefecture
    )


@pytest.fixture
def document_template():
    """Crée un template de document de test"""
    return DocumentTemplate.objects.create(
        titre="Template Maïs",
        description="Template pour culture de maïs",
        type_document="ITINERAIRE_TECHNIQUE",
        format_fichier="EXCEL",
        fichier_template="templates/test.xlsx",
        variables_requises=["canton", "culture", "prix"],
        version=1
    )


@pytest.fixture
def document_technique(document_template, region, prefecture, canton):
    """Crée un document technique de test"""
    return DocumentTechnique.objects.create(
        template=document_template,
        titre="Itinéraire Technique Maïs - Lomé",
        description="Guide complet pour la culture du maïs à Lomé",
        prix=Decimal("5000.00"),
        region=region,
        prefecture=prefecture,
        canton=canton,
        culture="Maïs",
        fichier_genere="documents/test.xlsx",
        actif=True
    )


@pytest.fixture
def multiple_documents(document_template, region, prefecture, canton):
    """Crée plusieurs documents de test"""
    documents = []
    
    # Document 1: Maïs
    doc1 = DocumentTechnique.objects.create(
        template=document_template,
        titre="Itinéraire Technique Maïs",
        description="Guide pour le maïs",
        prix=Decimal("5000.00"),
        region=region,
        prefecture=prefecture,
        canton=canton,
        culture="Maïs",
        fichier_genere="documents/mais.xlsx",
        actif=True
    )
    documents.append(doc1)
    
    # Document 2: Riz
    doc2 = DocumentTechnique.objects.create(
        template=document_template,
        titre="Itinéraire Technique Riz",
        description="Guide pour le riz",
        prix=Decimal("7000.00"),
        region=region,
        prefecture=prefecture,
        canton=canton,
        culture="Riz",
        fichier_genere="documents/riz.xlsx",
        actif=True
    )
    documents.append(doc2)
    
    # Document 3: Soja (inactif)
    doc3 = DocumentTechnique.objects.create(
        template=document_template,
        titre="Itinéraire Technique Soja",
        description="Guide pour le soja",
        prix=Decimal("6000.00"),
        region=region,
        prefecture=prefecture,
        canton=canton,
        culture="Soja",
        fichier_genere="documents/soja.xlsx",
        actif=False
    )
    documents.append(doc3)
    
    return documents


@pytest.mark.django_db
class TestDocumentTechniqueListAPI:
    """Tests pour l'endpoint de liste des documents"""
    
    def test_list_documents_success(self, api_client, document_technique, clear_cache):
        """Test: Récupération de la liste des documents"""
        url = reverse('document-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['titre'] == document_technique.titre
    
    def test_list_documents_only_active(self, api_client, multiple_documents, clear_cache):
        """Test: Seuls les documents actifs sont retournés"""
        url = reverse('document-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # Seulement les documents actifs
    
    def test_list_documents_pagination(self, api_client, document_template, region, prefecture, canton, clear_cache):
        """Test: Pagination des documents (50 par page)"""
        # Créer 60 documents
        for i in range(60):
            DocumentTechnique.objects.create(
                template=document_template,
                titre=f"Document {i}",
                description=f"Description {i}",
                prix=Decimal("5000.00"),
                region=region,
                prefecture=prefecture,
                canton=canton,
                culture="Maïs",
                fichier_genere=f"documents/doc{i}.xlsx",
                actif=True
            )
        
        url = reverse('document-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 50  # Page size = 50
        assert response.data['count'] == 60
        assert response.data['next'] is not None
    
    def test_filter_by_region(self, api_client, multiple_documents, region, clear_cache):
        """Test: Filtrage par région"""
        url = reverse('document-list')
        response = api_client.get(url, {'region': region.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_filter_by_canton(self, api_client, multiple_documents, canton, clear_cache):
        """Test: Filtrage par canton"""
        url = reverse('document-list')
        response = api_client.get(url, {'canton': canton.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_filter_by_culture(self, api_client, multiple_documents, clear_cache):
        """Test: Filtrage par culture"""
        url = reverse('document-list')
        response = api_client.get(url, {'culture': 'Maïs'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['culture'] == 'Maïs'
    
    def test_filter_by_type(self, api_client, document_technique, clear_cache):
        """Test: Filtrage par type de document"""
        url = reverse('document-list')
        response = api_client.get(url, {'type': 'ITINERAIRE_TECHNIQUE'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_filter_by_prix_range(self, api_client, multiple_documents, clear_cache):
        """Test: Filtrage par plage de prix"""
        url = reverse('document-list')
        response = api_client.get(url, {'prix_min': 6000, 'prix_max': 8000})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['culture'] == 'Riz'
    
    def test_search_by_titre(self, api_client, multiple_documents, clear_cache):
        """Test: Recherche par titre"""
        url = reverse('document-list')
        response = api_client.get(url, {'search': 'Riz'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert 'Riz' in response.data['results'][0]['titre']
    
    def test_ordering_by_prix(self, api_client, multiple_documents, clear_cache):
        """Test: Tri par prix"""
        url = reverse('document-list')
        response = api_client.get(url, {'ordering': 'prix'})
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert float(results[0]['prix']) <= float(results[1]['prix'])
    
    def test_ordering_by_prix_desc(self, api_client, multiple_documents, clear_cache):
        """Test: Tri par prix décroissant"""
        url = reverse('document-list')
        response = api_client.get(url, {'ordering': '-prix'})
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert float(results[0]['prix']) >= float(results[1]['prix'])
    
    def test_combined_filters(self, api_client, multiple_documents, region, clear_cache):
        """Test: Combinaison de plusieurs filtres"""
        url = reverse('document-list')
        response = api_client.get(url, {
            'region': region.id,
            'culture': 'Maïs',
            'prix_max': 6000
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['culture'] == 'Maïs'
    
    def test_list_response_structure(self, api_client, document_technique, clear_cache):
        """Test: Structure de la réponse de liste"""
        url = reverse('document-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        doc = response.data['results'][0]
        
        # Vérifier les champs requis
        required_fields = [
            'id', 'titre', 'description', 'prix',
            'region', 'region_nom', 'prefecture', 'prefecture_nom',
            'canton', 'canton_nom', 'culture',
            'type_document', 'format_fichier', 'created_at'
        ]
        for field in required_fields:
            assert field in doc


@pytest.mark.django_db
class TestDocumentTechniqueDetailAPI:
    """Tests pour l'endpoint de détail d'un document"""
    
    def test_retrieve_document_success(self, api_client, document_technique, clear_cache):
        """Test: Récupération des détails d'un document"""
        url = reverse('document-detail', kwargs={'pk': document_technique.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == document_technique.id
        assert response.data['titre'] == document_technique.titre
    
    def test_retrieve_document_not_found(self, api_client, clear_cache):
        """Test: Document inexistant"""
        url = reverse('document-detail', kwargs={'pk': 99999})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_detail_response_structure(self, api_client, document_technique, clear_cache):
        """Test: Structure de la réponse de détail"""
        url = reverse('document-detail', kwargs={'pk': document_technique.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier les champs requis
        required_fields = [
            'id', 'titre', 'description', 'prix',
            'region', 'region_nom', 'prefecture', 'prefecture_nom',
            'canton', 'canton_nom', 'culture',
            'type_document', 'type_document_display',
            'format_fichier', 'format_fichier_display',
            'template_info', 'actif', 'created_at', 'updated_at'
        ]
        for field in required_fields:
            assert field in response.data
    
    def test_detail_template_info(self, api_client, document_technique, clear_cache):
        """Test: Informations du template dans les détails"""
        url = reverse('document-detail', kwargs={'pk': document_technique.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        template_info = response.data['template_info']
        
        assert 'id' in template_info
        assert 'titre' in template_info
        assert 'version' in template_info
        assert template_info['titre'] == document_technique.template.titre


@pytest.mark.django_db
class TestDocumentCaching:
    """Tests pour le cache Redis"""
    
    def test_list_caching(self, api_client, document_technique, clear_cache):
        """Test: La liste des documents est mise en cache"""
        url = reverse('document-list')
        
        # Première requête - pas en cache
        response1 = api_client.get(url)
        assert response1.status_code == status.HTTP_200_OK
        
        # Modifier le document
        document_technique.titre = "Titre modifié"
        document_technique.save()
        
        # Deuxième requête - devrait retourner les données en cache (non modifiées)
        response2 = api_client.get(url)
        assert response2.status_code == status.HTTP_200_OK
        assert response2.data['results'][0]['titre'] != "Titre modifié"
        
        # Nettoyer le cache
        cache.clear()
        
        # Troisième requête - devrait retourner les nouvelles données
        response3 = api_client.get(url)
        assert response3.status_code == status.HTTP_200_OK
        assert response3.data['results'][0]['titre'] == "Titre modifié"
    
    def test_detail_caching(self, api_client, document_technique, clear_cache):
        """Test: Les détails d'un document sont mis en cache"""
        url = reverse('document-detail', kwargs={'pk': document_technique.id})
        
        # Première requête - pas en cache
        response1 = api_client.get(url)
        assert response1.status_code == status.HTTP_200_OK
        original_titre = response1.data['titre']
        
        # Modifier le document
        document_technique.titre = "Titre modifié"
        document_technique.save()
        
        # Deuxième requête - devrait retourner les données en cache
        response2 = api_client.get(url)
        assert response2.status_code == status.HTTP_200_OK
        assert response2.data['titre'] == original_titre
        
        # Nettoyer le cache
        cache.clear()
        
        # Troisième requête - devrait retourner les nouvelles données
        response3 = api_client.get(url)
        assert response3.status_code == status.HTTP_200_OK
        assert response3.data['titre'] == "Titre modifié"
    
    def test_different_filters_different_cache(self, api_client, multiple_documents, region, clear_cache):
        """Test: Différents filtres créent différentes entrées de cache"""
        url = reverse('document-list')
        
        # Requête 1: Sans filtre
        response1 = api_client.get(url)
        assert len(response1.data['results']) == 2
        
        # Requête 2: Avec filtre culture
        response2 = api_client.get(url, {'culture': 'Maïs'})
        assert len(response2.data['results']) == 1
        
        # Les deux réponses doivent être différentes
        assert len(response1.data['results']) != len(response2.data['results'])


@pytest.mark.django_db
class TestDocumentPermissions:
    """Tests pour les permissions"""
    
    def test_list_public_access(self, api_client, document_technique, clear_cache):
        """Test: La liste est accessible sans authentification"""
        url = reverse('document-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_detail_public_access(self, api_client, document_technique, clear_cache):
        """Test: Les détails sont accessibles sans authentification"""
        url = reverse('document-detail', kwargs={'pk': document_technique.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
