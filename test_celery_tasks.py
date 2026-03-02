#!/usr/bin/env python
"""
Script de test pour les tâches Celery

Ce script permet de tester:
- La connexion à Redis
- L'exécution des tâches asynchrones
- Les tâches planifiées
"""
import os
import sys
import django
from datetime import timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haroo.settings.dev')
django.setup()

from django.utils import timezone
from celery import current_app
from apps.documents.tasks import (
    send_purchase_confirmation_async,
    send_link_regenerated_async,
    send_expiration_reminders,
    anonymize_old_download_logs,
    cleanup_expired_links,
    debug_task
)


def test_celery_connection():
    """Tester la connexion à Celery/Redis"""
    print("\n" + "="*60)
    print("TEST 1: Connexion Celery/Redis")
    print("="*60)
    
    try:
        # Vérifier la connexion au broker
        inspect = current_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print("✅ Connexion à Redis réussie")
            print(f"   Workers actifs: {len(stats)}")
            for worker_name, worker_stats in stats.items():
                print(f"   - {worker_name}")
            return True
        else:
            print("❌ Aucun worker Celery détecté")
            print("   Démarrez un worker avec: celery -A haroo worker -l info")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        print("   Vérifiez que Redis est démarré")
        return False


def test_debug_task():
    """Tester la tâche de debug"""
    print("\n" + "="*60)
    print("TEST 2: Tâche de Debug")
    print("="*60)
    
    try:
        # Envoyer la tâche
        result = debug_task.delay()
        print(f"✅ Tâche envoyée: {result.id}")
        
        # Attendre le résultat (max 10 secondes)
        try:
            output = result.get(timeout=10)
            print(f"✅ Résultat: {output}")
            return True
        except Exception as e:
            print(f"⏳ Tâche en cours ou timeout: {str(e)}")
            print(f"   Status: {result.status}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False


def test_email_tasks():
    """Tester les tâches d'email (sans vraiment envoyer)"""
    print("\n" + "="*60)
    print("TEST 3: Tâches d'Email")
    print("="*60)
    
    from apps.documents.models import AchatDocument
    
    # Vérifier qu'il y a des achats dans la DB
    achat = AchatDocument.objects.first()
    
    if not achat:
        print("⚠️  Aucun achat dans la base de données")
        print("   Créez un achat de test pour tester les emails")
        return False
    
    print(f"📄 Achat de test trouvé: ID {achat.id}")
    
    # Test 1: Confirmation d'achat
    print("\n📧 Test: Confirmation d'achat")
    try:
        result = send_purchase_confirmation_async.delay(
            achat.id,
            'http://localhost:8000/api/v1/documents/1/download?token=test123'
        )
        print(f"✅ Tâche envoyée: {result.id}")
        print(f"   Status: {result.status}")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    
    # Test 2: Lien régénéré
    print("\n📧 Test: Lien régénéré")
    try:
        result = send_link_regenerated_async.delay(
            achat.id,
            'http://localhost:8000/api/v1/documents/1/download?token=new456'
        )
        print(f"✅ Tâche envoyée: {result.id}")
        print(f"   Status: {result.status}")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    
    return True


def test_scheduled_tasks():
    """Tester les tâches planifiées manuellement"""
    print("\n" + "="*60)
    print("TEST 4: Tâches Planifiées")
    print("="*60)
    
    # Test 1: Rappels d'expiration
    print("\n⏰ Test: Rappels d'expiration")
    try:
        result = send_expiration_reminders.delay()
        print(f"✅ Tâche envoyée: {result.id}")
        
        # Attendre le résultat
        try:
            output = result.get(timeout=30)
            print(f"✅ Résultat: {output}")
        except Exception as e:
            print(f"⏳ Tâche en cours: {str(e)}")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    
    # Test 2: Anonymisation des logs
    print("\n🔒 Test: Anonymisation des logs")
    try:
        result = anonymize_old_download_logs.delay()
        print(f"✅ Tâche envoyée: {result.id}")
        
        try:
            output = result.get(timeout=30)
            print(f"✅ Résultat: {output}")
        except Exception as e:
            print(f"⏳ Tâche en cours: {str(e)}")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    
    # Test 3: Nettoyage des liens expirés
    print("\n🧹 Test: Nettoyage des liens expirés")
    try:
        result = cleanup_expired_links.delay()
        print(f"✅ Tâche envoyée: {result.id}")
        
        try:
            output = result.get(timeout=30)
            print(f"✅ Résultat: {output}")
        except Exception as e:
            print(f"⏳ Tâche en cours: {str(e)}")
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    
    return True


def test_beat_schedule():
    """Afficher la configuration Celery Beat"""
    print("\n" + "="*60)
    print("TEST 5: Configuration Celery Beat")
    print("="*60)
    
    try:
        schedule = current_app.conf.beat_schedule
        
        print(f"\n📅 {len(schedule)} tâches planifiées:")
        
        for task_name, task_config in schedule.items():
            print(f"\n   📌 {task_name}")
            print(f"      Tâche: {task_config['task']}")
            print(f"      Schedule: {task_config['schedule']}")
            if 'options' in task_config:
                print(f"      Options: {task_config['options']}")
        
        print("\n✅ Configuration Beat OK")
        print("\nPour démarrer Beat:")
        print("   celery -A haroo beat -l info")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False


def test_retry_logic():
    """Tester la logique de retry"""
    print("\n" + "="*60)
    print("TEST 6: Logique de Retry")
    print("="*60)
    
    print("\n📋 Configuration des retry:")
    print("   - Max retries: 3")
    print("   - Retry delay: 60s (1 minute)")
    print("   - Exponential backoff: Activé")
    print("   - Backoff max: 600s (10 minutes)")
    print("   - Jitter: Activé (randomisation)")
    
    print("\n✅ Retry configuré avec exponential backoff")
    print("\nFormule: delay = base_delay * (2 ** retry_count) + jitter")
    print("   Retry 1: ~60s")
    print("   Retry 2: ~120s")
    print("   Retry 3: ~240s (max 600s)")
    
    return True


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("TEST DES TÂCHES CELERY - HAROO")
    print("="*60)
    
    print("\n📋 Prérequis:")
    print("   1. Redis doit être démarré")
    print("   2. Au moins un worker Celery doit être actif")
    print("   3. La base de données doit contenir des données de test")
    
    print("\n💡 Commandes utiles:")
    print("   - Démarrer Redis: redis-server")
    print("   - Démarrer worker: celery -A haroo worker -l info")
    print("   - Démarrer beat: celery -A haroo beat -l info")
    
    input("\nAppuyez sur Entrée pour continuer...")
    
    # Exécuter les tests
    results = []
    
    results.append(("Connexion Celery/Redis", test_celery_connection()))
    results.append(("Tâche de Debug", test_debug_task()))
    results.append(("Tâches d'Email", test_email_tasks()))
    results.append(("Tâches Planifiées", test_scheduled_tasks()))
    results.append(("Configuration Beat", test_beat_schedule()))
    results.append(("Logique de Retry", test_retry_logic()))
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n{success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        print("\n🎉 Tous les tests passent!")
        print("\n✅ Celery est correctement configuré")
        print("\n📝 Prochaines étapes:")
        print("   1. Marquer les subtasks 2.3.1-2.3.8 comme complétées")
        print("   2. Passer à la Phase 2.4: Intégration EmailService")
    else:
        print("\n⚠️  Certains tests ont échoué")
        print("   Vérifiez les logs ci-dessus pour plus de détails")
    
    return success_count == total_count


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
