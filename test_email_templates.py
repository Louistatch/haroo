#!/usr/bin/env python
"""
Script de test pour les templates d'emails

Ce script permet de:
1. Tester le rendu des templates
2. Générer des aperçus HTML
3. Envoyer des emails de test
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haroo.settings')
django.setup()

from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from apps.documents.models import DocumentTechnique, AchatDocument
from apps.users.models import User
from apps.payments.models import Transaction


def create_test_context():
    """Créer un contexte de test pour les templates"""
    
    # Créer ou récupérer un utilisateur de test
    user, _ = User.objects.get_or_create(
        phone_number='+22890000000',
        defaults={
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'email': 'jean.dupont@example.com',
            'user_type': 'EXPLOITANT'
        }
    )
    
    # Créer un document fictif
    class MockDocument:
        titre = "Compte d'exploitation - Maïs (Maritime)"
        culture = "Maïs"
        prix = 5000
    
    # Créer un achat fictif
    class MockAchat:
        format_fichier = "EXCEL"
        created_at = timezone.now()
        nombre_telechargements = 0
    
    document = MockDocument()
    achat = MockAchat()
    
    context = {
        'user': user,
        'document': document,
        'achat': achat,
        'download_url': 'http://localhost:8000/api/v1/documents/1/download?token=test_token_123',
        'expiration_date': timezone.now() + timedelta(hours=48),
        'frontend_url': 'http://localhost:5173',
        'purchase_history_url': 'http://localhost:5173/purchases',
        'hours_remaining': 24,
    }
    
    return context


def test_template(template_name, context, output_file=None):
    """
    Tester le rendu d'un template
    
    Args:
        template_name: Nom du template (ex: 'emails/purchase_confirmation.html')
        context: Contexte pour le template
        output_file: Fichier de sortie optionnel pour sauvegarder le HTML
    """
    print(f"\n{'='*60}")
    print(f"Test du template: {template_name}")
    print(f"{'='*60}")
    
    try:
        # Rendre le template
        html = render_to_string(template_name, context)
        
        print(f"✅ Template rendu avec succès!")
        print(f"   Taille: {len(html)} caractères")
        
        # Sauvegarder dans un fichier si demandé
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"   Sauvegardé dans: {output_file}")
        
        # Vérifier que le contenu contient les éléments clés
        checks = [
            ('Nom utilisateur', context['user'].first_name in html),
            ('Titre document', context['document'].titre in html),
            ('URL téléchargement', context['download_url'] in html),
            ('URL frontend', context['frontend_url'] in html),
        ]
        
        print(f"\n   Vérifications:")
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du rendu: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_all_templates():
    """Tester tous les templates d'emails"""
    
    print("\n" + "="*60)
    print("TEST DES TEMPLATES D'EMAILS")
    print("="*60)
    
    context = create_test_context()
    
    templates = [
        ('emails/purchase_confirmation.html', 'test_purchase_confirmation.html'),
        ('emails/purchase_confirmation.txt', 'test_purchase_confirmation.txt'),
        ('emails/expiration_reminder.html', 'test_expiration_reminder.html'),
        ('emails/expiration_reminder.txt', 'test_expiration_reminder.txt'),
        ('emails/link_regenerated.html', 'test_link_regenerated.html'),
        ('emails/link_regenerated.txt', 'test_link_regenerated.txt'),
    ]
    
    results = []
    for template_name, output_file in templates:
        result = test_template(template_name, context, output_file)
        results.append((template_name, result))
    
    # Résumé
    print(f"\n{'='*60}")
    print("RÉSUMÉ DES TESTS")
    print(f"{'='*60}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for template_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {template_name}")
    
    print(f"\n{success_count}/{total_count} templates testés avec succès")
    
    if success_count == total_count:
        print("\n🎉 Tous les templates fonctionnent correctement!")
        print("\nFichiers de test générés:")
        for _, output_file in templates:
            print(f"  - {output_file}")
        print("\nOuvrez les fichiers .html dans un navigateur pour voir le rendu.")
    else:
        print("\n⚠️  Certains templates ont des erreurs. Vérifiez les logs ci-dessus.")
    
    return success_count == total_count


def send_test_email():
    """Envoyer un email de test"""
    from apps.documents.services import EmailService
    
    print("\n" + "="*60)
    print("ENVOI D'EMAIL DE TEST")
    print("="*60)
    
    email_service = EmailService()
    context = create_test_context()
    
    print("\nConfiguration:")
    print(f"  From: {email_service.from_email}")
    print(f"  To: {context['user'].email}")
    
    response = input("\nVoulez-vous envoyer un email de test? (o/n): ")
    
    if response.lower() == 'o':
        # Créer un achat fictif pour le test
        print("\nEnvoi en cours...")
        
        # Note: Ceci nécessite un achat réel dans la base de données
        print("⚠️  Pour envoyer un vrai email, créez d'abord un achat dans la base de données.")
        print("    Utilisez le shell Django: python manage.py shell")
    else:
        print("Envoi annulé.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--send':
        send_test_email()
    else:
        success = test_all_templates()
        sys.exit(0 if success else 1)
