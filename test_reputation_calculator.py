"""
Test simple pour vérifier le ReputationCalculator
Sans dépendances PostGIS
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haroo.settings')
django.setup()

from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.locations.models import Region, Prefecture, Canton
from apps.missions.models import Mission
from apps.ratings.models import Notation
from apps.ratings.services import ReputationCalculator
from apps.users.models import AgronomeProfile, ExploitantProfile

User = get_user_model()

def test_reputation_calculator():
    """Test du calcul de réputation"""
    print("=== Test du ReputationCalculator ===\n")
    
    # Créer les données géographiques
    region = Region.objects.create(nom="Maritime", code="MAR")
    prefecture = Prefecture.objects.create(nom="Golfe", code="GOL", region=region)
    canton = Canton.objects.create(nom="Lomé 1er", code="LOM1", prefecture=prefecture)
    
    # Créer un agronome
    agronome = User.objects.create_user(
        username='agronome_test@test.com',
        email='agronome_test@test.com',
        password='Test1234!',
        phone_number='+22890999001',
        user_type='AGRONOME',
        first_name='Marie',
        last_name='Test'
    )
    
    agronome_profile = AgronomeProfile.objects.create(
        user=agronome,
        canton_rattachement=canton,
        specialisations=['Maraîchage'],
        statut_validation='VALIDE',
        badge_valide=True
    )
    
    print(f"Agronome créé: {agronome.get_full_name()}")
    print(f"Note initiale: {agronome_profile.note_moyenne}")
    print(f"Nombre d'avis initial: {agronome_profile.nombre_avis}\n")
    
    # Créer des exploitants
    exploitants = []
    for i in range(3):
        exp = User.objects.create_user(
            username=f'exploitant{i}@test.com',
            password='Test1234!',
            phone_number=f'+2289099900{i+2}',
            user_type='EXPLOITANT',
            first_name=f'Exploitant{i}',
            last_name='Test'
        )
        
        ExploitantProfile.objects.create(
            user=exp,
            superficie_totale=Decimal('15.00'),
            canton_principal=canton,
            coordonnees_gps='{"type": "Point", "coordinates": [1.2, 6.1]}',
            statut_verification='VERIFIE'
        )
        exploitants.append(exp)
    
    # Créer des missions terminées et des notations
    notes = [5, 4, 5]  # Moyenne attendue: 4.67
    
    for i, (exp, note) in enumerate(zip(exploitants, notes)):
        mission = Mission.objects.create(
            exploitant=exp,
            agronome=agronome,
            description=f"Mission {i+1}",
            budget_propose=Decimal('50000.00'),
            statut='TERMINEE'
        )
        
        notation = Notation.objects.create(
            notateur=exp,
            note=agronome,
            note_valeur=note,
            commentaire=f"Commentaire de test numéro {i+1} avec plus de 20 caractères.",
            mission=mission,
            statut='PUBLIE'
        )
        
        print(f"Notation {i+1} créée: {note} étoiles")
    
    # Calculer la note moyenne
    print("\n--- Calcul de la note moyenne ---")
    moyenne, nombre = ReputationCalculator.update_user_rating(agronome)
    
    print(f"Note moyenne calculée: {moyenne}")
    print(f"Nombre d'avis: {nombre}")
    
    # Vérifier que le profil a été mis à jour
    agronome_profile.refresh_from_db()
    print(f"\nNote moyenne dans le profil: {agronome_profile.note_moyenne}")
    print(f"Nombre d'avis dans le profil: {agronome_profile.nombre_avis}")
    
    # Vérifications
    expected_moyenne = Decimal('4.67')
    assert agronome_profile.note_moyenne == expected_moyenne, f"Erreur: attendu {expected_moyenne}, obtenu {agronome_profile.note_moyenne}"
    assert agronome_profile.nombre_avis == 3, f"Erreur: attendu 3 avis, obtenu {agronome_profile.nombre_avis}"
    assert moyenne == expected_moyenne, f"Erreur: moyenne retournée {moyenne} != {expected_moyenne}"
    assert nombre == 3, f"Erreur: nombre retourné {nombre} != 3"
    
    print("\n✓ Tous les tests passent!")
    print("✓ Le calcul de la note moyenne fonctionne correctement")
    print("✓ La note est arrondie à 2 décimales (Exigence 27.3)")
    print("✓ Le profil est mis à jour automatiquement (Exigence 27.3)")
    
    # Tester get_user_rating
    print("\n--- Test de get_user_rating ---")
    rating_info = ReputationCalculator.get_user_rating(agronome)
    print(f"Note moyenne: {rating_info['note_moyenne']}")
    print(f"Nombre d'avis: {rating_info['nombre_avis']}")
    
    assert rating_info['note_moyenne'] == float(expected_moyenne)
    assert rating_info['nombre_avis'] == 3
    
    print("\n✓ get_user_rating fonctionne correctement")
    
    # Nettoyer
    Notation.objects.all().delete()
    Mission.objects.all().delete()
    User.objects.filter(username__contains='test').delete()
    Canton.objects.all().delete()
    Prefecture.objects.all().delete()
    Region.objects.all().delete()
    
    print("\n=== Test terminé avec succès ===")

if __name__ == '__main__':
    test_reputation_calculator()
