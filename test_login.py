import requests
import json

# Test de connexion avec les utilisateurs demo
base_url = "http://127.0.0.1:8000/api/v1"

test_users = [
    {
        "phone_number": "+22890000001",
        "password": "Demo123!",
        "name": "exploitant_demo"
    },
    {
        "phone_number": "+22890000002",
        "password": "Demo123!",
        "name": "agronome_demo"
    },
    {
        "phone_number": "+22890000003",
        "password": "Admin123!",
        "name": "admin_demo"
    }
]

print("=== TEST DE CONNEXION API ===\n")

for user in test_users:
    print(f"Test connexion: {user['name']}")
    print(f"Phone: {user['phone_number']}")
    print(f"Password: {user['password']}")
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            json={
                "phone_number": user['phone_number'],
                "password": user['password']
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Text: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✅ CONNEXION RÉUSSIE")
        else:
            print("❌ CONNEXION ÉCHOUÉE")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERREUR: Impossible de se connecter au serveur")
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
    
    print("-" * 60)
    print()
