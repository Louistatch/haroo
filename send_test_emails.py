#!/usr/bin/env python
"""
Script pour envoyer des emails de test
Permet de tester les templates sur différents clients email
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haroo.settings.dev')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone


def create_test_context():
    """Créer un contexte de test pour les templates"""
    
    class MockUser:
        first_name = "Jean"
        last_name = "Dupont"
        email = "test@example.com"  # Changez ceci pour votre email de test
    
    class MockDocument:
        titre = "Compte d'exploitation - Maïs (Maritime)"
        culture = "Maïs"
        prix = 5000
    
    class MockAchat:
        format_fichier = "EXCEL"
        created_at = timezone.now()
        nombre_telechargements = 0
    
    user = MockUser()
    document = MockDocument()
    achat = MockAchat()
    
    context = {
        'user': user,
        'document': document,
        'achat': achat,
        'download_url': 'http://localhost:8000/api/v1/documents/1/download?token=test_token_abc123xyz',
        'expiration_date': timezone.now() + timedelta(hours=48),
        'frontend_url': 'http://localhost:5173',
        'purchase_history_url': 'http://localhost:5173/purchases',
        'hours_remaining': 24,
    }
    
    return context


def send_email(template_html, template_txt, subject, to_email, context):
    """
    Envoyer un email de test
    
    Args:
        template_html: Nom du template HTML
        template_txt: Nom du template texte
        subject: Sujet de l'email
        to_email: Adresse email destinataire
        context: Contexte pour les templates
    """
    try:
        # Rendre les templates
        html_content = render_to_string(template_html, context)
        text_content = render_to_string(template_txt, context)
        
        # Créer l'email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email='noreply@haroo.tg',
            to=[to_email]
        )
        email.attach_alternative(html_content, "text/html")
        
        # Envoyer
        email.send(fail_silently=False)
        
        print(f"✅ Email envoyé: {subject}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    
    print("\n" + "="*60)
    print("ENVOI D'EMAILS DE TEST - HAROO")
    print("="*60)
    
    # Demander l'email de destination
    print("\n📧 Configuration")
    print("-" * 60)
    
    default_email = "test@example.com"
    to_email = input(f"Email destinataire [{default_email}]: ").strip()
    if not to_email:
        to_email = default_email
    
    print(f"\n✉️  Les emails seront envoyés à: {to_email}")
    
    # Vérifier la configuration email Django
    from django.conf import settings
    print(f"\n⚙️  Configuration Django:")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Non configuré')}")
    print(f"   EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Non configuré')}")
    
    # Demander confirmation
    print("\n" + "="*60)
    response = input("\nEnvoyer les 3 emails de test? (o/n): ")
    
    if response.lower() != 'o':
        print("❌ Envoi annulé.")
        return
    
    # Créer le contexte
    context = create_test_context()
    
    # Liste des emails à envoyer
    emails_to_send = [
        {
            'template_html': 'emails/purchase_confirmation.html',
            'template_txt': 'emails/purchase_confirmation.txt',
            'subject': "Confirmation d'achat - Compte d'exploitation Maïs",
            'description': '1. Confirmation d\'achat'
        },
        {
            'template_html': 'emails/expiration_reminder.html',
            'template_txt': 'emails/expiration_reminder.txt',
            'subject': "Rappel: Votre lien de téléchargement expire bientôt",
            'description': '2. Rappel d\'expiration'
        },
        {
            'template_html': 'emails/link_regenerated.html',
            'template_txt': 'emails/link_regenerated.txt',
            'subject': "Nouveau lien de téléchargement - Compte d'exploitation Maïs",
            'description': '3. Lien régénéré'
        }
    ]
    
    # Envoyer les emails
    print("\n" + "="*60)
    print("ENVOI EN COURS")
    print("="*60 + "\n")
    
    results = []
    for email_config in emails_to_send:
        print(f"📤 {email_config['description']}...")
        success = send_email(
            email_config['template_html'],
            email_config['template_txt'],
            email_config['subject'],
            to_email,
            context
        )
        results.append((email_config['description'], success))
        print()
    
    # Résumé
    print("="*60)
    print("RÉSUMÉ")
    print("="*60)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for description, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {description}")
    
    print(f"\n{success_count}/{total_count} emails envoyés avec succès")
    
    if success_count == total_count:
        print("\n🎉 Tous les emails ont été envoyés!")
        print("\n📋 Prochaines étapes:")
        print("   1. Vérifiez votre boîte de réception")
        print("   2. Testez sur Gmail (web + mobile)")
        print("   3. Testez sur Outlook (desktop + web)")
        print("   4. Testez sur Apple Mail (si disponible)")
        print("   5. Vérifiez:")
        print("      - Le branding Haroo est correct")
        print("      - Les couleurs vertes s'affichent bien")
        print("      - Les boutons sont cliquables")
        print("      - Le responsive fonctionne sur mobile")
        print("      - Les liens fonctionnent")
        print("\n📝 Documentez les résultats dans tasks.md")
    else:
        print("\n⚠️  Certains emails n'ont pas pu être envoyés.")
        print("   Vérifiez la configuration EMAIL dans settings.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Envoi interrompu par l'utilisateur.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
