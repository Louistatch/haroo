#!/usr/bin/env python
"""
Script de test rapide pour vérifier l'API des documents
"""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

def test_documents_list():
    """Tester l'endpoint de liste des documents"""
    print("🔍 Test de l'API Documents...")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/documents/", timeout=5)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès!")
            print(f"Nombre de documents: {data.get('count', 0)}")
            
            if data.get('results'):
                print(f"\nPremier document:")
                doc = data['results'][0]
                print(f"  - ID: {doc.get('id')}")
                print(f"  - Titre: {doc.get('titre')}")
                print(f"  - Prix: {doc.get('prix')} FCFA")
                print(f"  - Culture: {doc.get('culture')}")
            else:
                print("⚠️  Aucun document trouvé dans la base de données")
                print("\nPour créer des documents de test, exécutez:")
                print("  python manage.py shell")
                print("  >>> from apps.documents.models import DocumentTechnique")
                print("  >>> # Créer des documents...")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"Réponse: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("\nAssurez-vous que le serveur Django est démarré:")
        print("  python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    
    print("-" * 50)

def test_server_health():
    """Vérifier que le serveur répond"""
    print("\n🏥 Test de santé du serveur...")
    print("-" * 50)
    
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        print(f"✅ Serveur accessible (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Serveur inaccessible")
        print("\nDémarrez le serveur avec:")
        print("  python manage.py runserver")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    
    print("-" * 50)

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  TEST API DOCUMENTS - Plateforme Agricole Togo")
    print("=" * 50 + "\n")
    
    test_server_health()
    test_documents_list()
    
    print("\n✨ Tests terminés!\n")
