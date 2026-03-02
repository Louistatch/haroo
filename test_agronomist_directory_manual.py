"""
Script de test manuel pour l'annuaire des agronomes
Exigences: 8.1, 8.2, 8.3, 8.4

Ce script teste l'endpoint GET /api/v1/agronomists sans Redis
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haroo.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from apps.locations.models import Region, Prefecture, Canton
from apps.users.models import AgronomeProfile

User = get_user_model()

def setup_test_data():
    """Crée des données de test"""
    print("🔧 Création des données de test...")
    
    # Créer la localisation
    try:
        region = Region.objects.get(code="MAR_TEST")
    except Region.DoesNotExist:
        region = Region.objects.create(nom="Région Maritime Test", code="MAR_TEST")
    
    try:
        prefecture = Prefecture.objects.get(code="GOL_TEST")
    except Prefecture.DoesNotExist:
        prefecture = Prefecture.objects.create(
            nom="Golfe Test",
            region=region,
            code="GOL_TEST"
        )
    
    try:
        canton1 = Canton.objects.get(code="LOM1_TEST")
    except Canton.DoesNotExist:
        canton1 = Canton.objects.create(
            nom="Lomé 1er Test",
            prefecture=prefecture,
            code="LOM1_TEST"
        )
    
    try:
        canton2 = Canton.objects.get(code="LOM2_TEST")
    except Canton.DoesNotExist:
        canton2 = Canton.objects.create(
            nom="Lomé 2ème Test",
            prefecture=prefecture,
            code="LOM2_TEST"
        )
    
    # Créer des agronomes validés
    if not User.objects.filter(username='test_agro1').exists():
        user1 = User.objects.create_user(
            username='test_agro1',
            email='test_agro1@test.com',
            phone_number='+22891000001',
            password='Test@1234',
            user_type='AGRONOME',
            first_name='Jean',
            last_name='Dupont'
        )
        AgronomeProfile.objects.create(
            user=user1,
            canton_rattachement=canton1,
            specialisations=['Cultures céréalières', 'Irrigation'],
            statut_validation='VALIDE',
            badge_valide=True,
            note_moyenne=4.5,
            nombre_avis=10
        )
        print("✅ Agronome 1 créé: Jean Dupont (Lomé 1er)")
    
    if not User.objects.filter(username='test_agro2').exists():
        user2 = User.objects.create_user(
            username='test_agro2',
            email='test_agro2@test.com',
            phone_number='+22891000002',
            password='Test@1234',
            user_type='AGRONOME',
            first_name='Marie',
            last_name='Martin'
        )
        AgronomeProfile.objects.create(
            user=user2,
            canton_rattachement=canton2,
            specialisations=['Cultures maraîchères', 'Agriculture biologique'],
            statut_validation='VALIDE',
            badge_valide=True,
            note_moyenne=4.8,
            nombre_avis=15
        )
        print("✅ Agronome 2 créé: Marie Martin (Lomé 2ème)")
    
    # Créer un agronome en attente (ne doit pas apparaître)
    if not User.objects.filter(username='test_agro3').exists():
        user3 = User.objects.create_user(
            username='test_agro3',
            email='test_agro3@test.com',
            phone_number='+22891000003',
            password='Test@1234',
            user_type='AGRONOME',
            first_name='Paul',
            last_name='Bernard'
        )
        AgronomeProfile.objects.create(
            user=user3,
            canton_rattachement=canton1,
            specialisations=['Élevage bovin'],
            statut_validation='EN_ATTENTE',
            badge_valide=False
        )
        print("✅ Agronome 3 créé: Paul Bernard (EN_ATTENTE - ne doit pas apparaître)")
    
    return {
        'region': region,
        'prefecture': prefecture,
        'canton1': canton1,
        'canton2': canton2
    }


def test_directory():
    """Teste l'annuaire des agronomes"""
    from django.test import RequestFactory
    from apps.users.views import agronomist_directory
    
    factory = RequestFactory()
    
    print("\n📋 Test 1: Liste tous les agronomes validés")
    request = factory.get('/api/v1/agronomists')
    response = agronomist_directory(request)
    
    if response.status_code == 200:
        data = response.data
        print(f"✅ Statut: {response.status_code}")
        print(f"   Nombre total: {data['count']}")
        print(f"   Résultats sur cette page: {len(data['results'])}")
        
        for agro in data['results']:
            print(f"\n   - {agro['nom_complet']}")
            print(f"     Canton: {agro['canton_nom']}")
            print(f"     Spécialisations: {', '.join(agro['specialisations'])}")
            print(f"     Note: {agro['note_moyenne']} ({agro['nombre_avis']} avis)")
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(f"   {response.data}")
    
    print("\n📋 Test 2: Filtrer par canton")
    locations = setup_test_data()
    request = factory.get(f'/api/v1/agronomists?canton={locations["canton1"].id}')
    response = agronomist_directory(request)
    
    if response.status_code == 200:
        data = response.data
        print(f"✅ Statut: {response.status_code}")
        print(f"   Nombre d'agronomes dans {locations['canton1'].nom}: {data['count']}")
        
        for agro in data['results']:
            print(f"   - {agro['nom_complet']} ({agro['canton_nom']})")
    else:
        print(f"❌ Erreur: {response.status_code}")
    
    print("\n📋 Test 3: Filtrer par spécialisation")
    request = factory.get('/api/v1/agronomists?specialisation=Irrigation')
    response = agronomist_directory(request)
    
    if response.status_code == 200:
        data = response.data
        print(f"✅ Statut: {response.status_code}")
        print(f"   Nombre d'agronomes avec spécialisation 'Irrigation': {data['count']}")
        
        for agro in data['results']:
            print(f"   - {agro['nom_complet']}")
            print(f"     Spécialisations: {', '.join(agro['specialisations'])}")
    else:
        print(f"❌ Erreur: {response.status_code}")
    
    print("\n📋 Test 4: Pagination")
    request = factory.get('/api/v1/agronomists?page=1&page_size=1')
    response = agronomist_directory(request)
    
    if response.status_code == 200:
        data = response.data
        print(f"✅ Statut: {response.status_code}")
        print(f"   Page: {data['current_page']}/{data['num_pages']}")
        print(f"   Taille de page: {data['page_size']}")
        print(f"   Page suivante: {data['next']}")
        print(f"   Page précédente: {data['previous']}")
    else:
        print(f"❌ Erreur: {response.status_code}")


if __name__ == '__main__':
    print("=" * 60)
    print("TEST MANUEL - ANNUAIRE DES AGRONOMES")
    print("Exigences: 8.1, 8.2, 8.3, 8.4")
    print("=" * 60)
    
    setup_test_data()
    test_directory()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés!")
    print("=" * 60)
