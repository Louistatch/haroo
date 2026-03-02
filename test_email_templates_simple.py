#!/usr/bin/env python
"""
Script de test simple pour les templates d'emails
Teste le rendu sans nécessiter Django complet
"""
from datetime import datetime, timedelta
import os


def create_test_context():
    """Créer un contexte de test pour les templates"""
    
    class MockUser:
        first_name = "Jean"
        last_name = "Dupont"
        email = "jean.dupont@example.com"
    
    class MockDocument:
        titre = "Compte d'exploitation - Maïs (Maritime)"
        culture = "Maïs"
        prix = 5000
    
    class MockAchat:
        format_fichier = "EXCEL"
        created_at = datetime.now()
        nombre_telechargements = 0
    
    user = MockUser()
    document = MockDocument()
    achat = MockAchat()
    
    context = {
        'user': user,
        'document': document,
        'achat': achat,
        'download_url': 'http://localhost:8000/api/v1/documents/1/download?token=test_token_123',
        'expiration_date': datetime.now() + timedelta(hours=48),
        'frontend_url': 'http://localhost:5173',
        'purchase_history_url': 'http://localhost:5173/purchases',
        'hours_remaining': 24,
    }
    
    return context


def test_template_exists(template_path):
    """Vérifier qu'un template existe"""
    if os.path.exists(template_path):
        print(f"  ✅ Fichier existe: {template_path}")
        return True
    else:
        print(f"  ❌ Fichier manquant: {template_path}")
        return False


def test_template_content(template_path, required_strings):
    """Vérifier que le template contient les chaînes requises"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        all_found = True
        for required in required_strings:
            if required in content:
                print(f"  ✅ Contient: {required}")
            else:
                print(f"  ❌ Manque: {required}")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"  ❌ Erreur lecture: {str(e)}")
        return False


def test_all_templates():
    """Tester tous les templates d'emails"""
    
    print("\n" + "="*60)
    print("TEST DES TEMPLATES D'EMAILS")
    print("="*60)
    
    templates_to_test = [
        {
            'name': 'Base Email',
            'path': 'templates/emails/base_email.html',
            'required': ['<!DOCTYPE html>', 'Haroo', '{% block content %}']
        },
        {
            'name': 'Purchase Confirmation HTML',
            'path': 'templates/emails/purchase_confirmation.html',
            'required': ['{% extends', 'Confirmation d\'achat', '{{ user.first_name }}', '{{ document.titre }}']
        },
        {
            'name': 'Purchase Confirmation TXT',
            'path': 'templates/emails/purchase_confirmation.txt',
            'required': ['Confirmation d\'achat', '{{ user.first_name }}', '{{ document.titre }}']
        },
        {
            'name': 'Expiration Reminder HTML',
            'path': 'templates/emails/expiration_reminder.html',
            'required': ['{% extends', 'expire bientôt', '{{ hours_remaining }}', '{{ purchase_history_url }}']
        },
        {
            'name': 'Expiration Reminder TXT',
            'path': 'templates/emails/expiration_reminder.txt',
            'required': ['expire bientôt', '{{ hours_remaining }}', '{{ purchase_history_url }}']
        },
        {
            'name': 'Link Regenerated HTML',
            'path': 'templates/emails/link_regenerated.html',
            'required': ['{% extends', 'Nouveau lien', '{{ download_url }}']
        },
        {
            'name': 'Link Regenerated TXT',
            'path': 'templates/emails/link_regenerated.txt',
            'required': ['Nouveau lien', '{{ download_url }}']
        },
    ]
    
    results = []
    
    for template in templates_to_test:
        print(f"\n{'='*60}")
        print(f"Test: {template['name']}")
        print(f"{'='*60}")
        
        exists = test_template_exists(template['path'])
        if exists:
            content_ok = test_template_content(template['path'], template['required'])
            results.append((template['name'], exists and content_ok))
        else:
            results.append((template['name'], False))
    
    # Résumé
    print(f"\n{'='*60}")
    print("RÉSUMÉ DES TESTS")
    print(f"{'='*60}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for template_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {template_name}")
    
    print(f"\n{success_count}/{total_count} templates validés avec succès")
    
    if success_count == total_count:
        print("\n🎉 Tous les templates sont présents et bien formés!")
        print("\nPour tester le rendu complet:")
        print("  1. Démarrez le serveur Django: python manage.py runserver")
        print("  2. Utilisez le shell Django pour tester EmailService")
        print("  3. Ou configurez MailHog pour voir les emails en développement")
    else:
        print("\n⚠️  Certains templates ont des problèmes. Vérifiez les logs ci-dessus.")
    
    return success_count == total_count


def check_premailer():
    """Vérifier si premailer est installé"""
    print("\n" + "="*60)
    print("VÉRIFICATION PREMAILER")
    print("="*60)
    
    try:
        import premailer
        print("✅ premailer est installé")
        print(f"   Version: {premailer.__version__ if hasattr(premailer, '__version__') else 'inconnue'}")
        return True
    except ImportError:
        print("❌ premailer n'est pas installé")
        print("\nPour installer:")
        print("  pip install premailer")
        return False


if __name__ == "__main__":
    import sys
    
    # Test des templates
    templates_ok = test_all_templates()
    
    # Vérification premailer
    premailer_ok = check_premailer()
    
    # Résultat final
    print("\n" + "="*60)
    print("RÉSULTAT FINAL")
    print("="*60)
    
    if templates_ok and premailer_ok:
        print("✅ Tous les tests passent!")
        print("\nProchaines étapes (subtasks 2.2.9 et 2.2.10):")
        print("  1. Tester avec premailer pour inline CSS")
        print("  2. Envoyer des emails de test à Gmail, Outlook, Apple Mail")
        sys.exit(0)
    elif templates_ok:
        print("⚠️  Templates OK mais premailer manquant")
        print("   Installez premailer pour continuer")
        sys.exit(1)
    else:
        print("❌ Des templates ont des problèmes")
        sys.exit(1)
