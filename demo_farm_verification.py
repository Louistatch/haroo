"""
Script de démonstration du workflow de validation des exploitations
Exigences: 10.4, 10.5, 10.6
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_response(title, response):
    """Affiche une réponse formatée"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print()


def demo_farm_verification_workflow():
    """
    Démontre le workflow complet de validation d'exploitation
    """
    print("\n" + "="*60)
    print("DÉMONSTRATION: Workflow de Validation des Exploitations")
    print("="*60)
    
    # 1. Connexion admin
    print("\n1. Connexion en tant qu'administrateur...")
    admin_login = requests.post(f"{BASE_URL}/auth/login", json={
        "phone_number": "+22890000001",
        "password": "Admin@123"
    })
    
    if admin_login.status_code != 200:
        print("❌ Erreur de connexion admin")
        return
    
    admin_token = admin_login.json()['tokens']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Connexion admin réussie")
    
    # 2. Récupérer la liste des exploitations en attente
    print("\n2. Récupération des exploitations en attente de vérification...")
    pending_response = requests.get(
        f"{BASE_URL}/farms/pending",
        headers=admin_headers
    )
    print_response("Liste des exploitations en attente", pending_response)
    
    if pending_response.status_code == 200 and pending_response.json()['count'] > 0:
        farm_id = pending_response.json()['profiles'][0]['id']
        
        # 3. Consulter les détails d'une exploitation
        print(f"\n3. Consultation des détails de l'exploitation {farm_id}...")
        details_response = requests.get(
            f"{BASE_URL}/farms/{farm_id}/details",
            headers=admin_headers
        )
        print_response(f"Détails de l'exploitation {farm_id}", details_response)
        
        # 4. Valider l'exploitation
        print(f"\n4. Validation de l'exploitation {farm_id}...")
        verify_response = requests.post(
            f"{BASE_URL}/farms/{farm_id}/verify",
            headers=admin_headers,
            json={
                "approved": True
            }
        )
        print_response("Résultat de la validation", verify_response)
        
        if verify_response.status_code == 200:
            print("✅ Exploitation vérifiée avec succès!")
            print("✅ Fonctionnalités premium débloquées:")
            print("   - Dashboard avancé")
            print("   - Recrutement d'agronomes")
            print("   - Recrutement d'ouvriers")
            print("   - Préventes agricoles")
            print("   - Analyses de marché")
            print("   - Optimisation logistique")
            print("   - Recommandations de cultures")
            print("   - Irrigation intelligente")
    else:
        print("ℹ️  Aucune exploitation en attente de vérification")
        print("\nCréation d'une exploitation de test...")
        
        # Créer un exploitant de test
        exploitant_register = requests.post(f"{BASE_URL}/auth/register", json={
            "username": "exploitant_demo",
            "email": "exploitant_demo@test.com",
            "phone_number": "+22890999999",
            "password": "Test@123",
            "password_confirm": "Test@123",
            "user_type": "EXPLOITANT",
            "first_name": "Demo",
            "last_name": "Exploitant"
        })
        
        if exploitant_register.status_code == 201:
            print("✅ Exploitant de test créé")
            print("ℹ️  Vous pouvez maintenant soumettre une demande de vérification")
            print("   via POST /api/v1/farms/verification-request")


def demo_farm_rejection():
    """
    Démontre le rejet d'une exploitation avec motif
    """
    print("\n" + "="*60)
    print("DÉMONSTRATION: Rejet d'une Exploitation")
    print("="*60)
    
    # Connexion admin
    admin_login = requests.post(f"{BASE_URL}/auth/login", json={
        "phone_number": "+22890000001",
        "password": "Admin@123"
    })
    
    if admin_login.status_code != 200:
        print("❌ Erreur de connexion admin")
        return
    
    admin_token = admin_login.json()['tokens']['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Récupérer une exploitation en attente
    pending_response = requests.get(
        f"{BASE_URL}/farms/pending",
        headers=admin_headers
    )
    
    if pending_response.status_code == 200 and pending_response.json()['count'] > 0:
        farm_id = pending_response.json()['profiles'][0]['id']
        
        print(f"\nRejet de l'exploitation {farm_id} avec motif...")
        reject_response = requests.post(
            f"{BASE_URL}/farms/{farm_id}/verify",
            headers=admin_headers,
            json={
                "approved": False,
                "motif_rejet": "Documents justificatifs insuffisants. Veuillez fournir le titre foncier et des photos aériennes récentes de l'exploitation."
            }
        )
        print_response("Résultat du rejet", reject_response)
        
        if reject_response.status_code == 200:
            print("✅ Exploitation rejetée avec motif")
            print("✅ Notification envoyée à l'exploitant avec le motif détaillé")
    else:
        print("ℹ️  Aucune exploitation en attente pour démonstration du rejet")


def demo_premium_features_check():
    """
    Démontre la vérification des fonctionnalités premium
    """
    print("\n" + "="*60)
    print("DÉMONSTRATION: Vérification des Fonctionnalités Premium")
    print("="*60)
    
    # Connexion exploitant
    print("\n1. Connexion en tant qu'exploitant...")
    exploitant_login = requests.post(f"{BASE_URL}/auth/login", json={
        "phone_number": "+22890000002",
        "password": "Test@123"
    })
    
    if exploitant_login.status_code != 200:
        print("❌ Erreur de connexion exploitant")
        return
    
    exploitant_token = exploitant_login.json()['tokens']['access_token']
    exploitant_headers = {"Authorization": f"Bearer {exploitant_token}"}
    print("✅ Connexion exploitant réussie")
    
    # Vérifier les fonctionnalités premium
    print("\n2. Vérification des fonctionnalités premium disponibles...")
    features_response = requests.get(
        f"{BASE_URL}/farms/me/premium-features",
        headers=exploitant_headers
    )
    print_response("Fonctionnalités Premium", features_response)
    
    if features_response.status_code == 200:
        data = features_response.json()
        if data['is_verified']:
            print("✅ Exploitation vérifiée - Toutes les fonctionnalités premium sont débloquées")
        else:
            print(f"ℹ️  Statut: {data['statut_verification']}")
            print(f"ℹ️  {data.get('message', '')}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print(" "*20 + "DÉMONSTRATION DU WORKFLOW DE VALIDATION")
    print(" "*25 + "DES EXPLOITATIONS AGRICOLES")
    print("="*80)
    print("\nExigences: 10.4, 10.5, 10.6")
    print("\nCe script démontre:")
    print("  1. La récupération des exploitations en attente")
    print("  2. La consultation des détails d'une exploitation")
    print("  3. La validation d'une exploitation (déblocage des fonctionnalités premium)")
    print("  4. Le rejet d'une exploitation avec motif")
    print("  5. La vérification des fonctionnalités premium")
    
    print("\n" + "="*80)
    print("PRÉREQUIS:")
    print("  - Le serveur Django doit être lancé sur http://localhost:8000")
    print("  - Un compte admin doit exister (phone: +22890000001, password: Admin@123)")
    print("  - Des exploitations en attente de vérification doivent exister")
    print("="*80)
    
    input("\nAppuyez sur Entrée pour commencer la démonstration...")
    
    try:
        # Démonstration 1: Workflow de validation
        demo_farm_verification_workflow()
        
        input("\nAppuyez sur Entrée pour voir la démonstration du rejet...")
        
        # Démonstration 2: Rejet avec motif
        demo_farm_rejection()
        
        input("\nAppuyez sur Entrée pour vérifier les fonctionnalités premium...")
        
        # Démonstration 3: Vérification des fonctionnalités premium
        demo_premium_features_check()
        
        print("\n" + "="*80)
        print("DÉMONSTRATION TERMINÉE")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERREUR: Impossible de se connecter au serveur")
        print("Assurez-vous que le serveur Django est lancé sur http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
