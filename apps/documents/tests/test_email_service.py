"""
Tests pour le service d'email
"""
from django.test import TestCase, override_settings
from django.core import mail
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock

from apps.documents.services import EmailService
from apps.documents.models import (
    DocumentTemplate,
    DocumentTechnique,
    AchatDocument
)
from apps.users.models import User
from apps.payments.models import Transaction
from apps.locations.models import Region, Prefecture, Canton


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    FRONTEND_URL='http://localhost:5173'
)
class EmailServiceTest(TestCase):
    """Tests pour EmailService"""
    
    def setUp(self):
        """Préparer les données de test"""
        # Créer un utilisateur
        self.user = User.objects.create_user(
            phone_number='+22890123456',
            password='testpass123',
            first_name='Jean',
            last_name='Dupont',
            email='jean.dupont@example.com',
            user_type='EXPLOITANT'
        )
        
        # Créer une localisation
        self.region = Region.objects.create(nom='Maritime')
        self.prefecture = Prefecture.objects.create(
            nom='Golfe',
            region=self.region
        )
        self.canton = Canton.objects.create(
            nom='Lomé',
            prefecture=self.prefecture
        )
        
        # Créer un template
        self.template = DocumentTemplate.objects.create(
            titre='Template Test',
            type_document='COMPTE_EXPLOITATION',
            format_fichier='EXCEL',
            fichier_template='templates/test.xlsx'
        )
        
        # Créer un document
        self.document = DocumentTechnique.objects.create(
            template=self.template,
            titre='Document Test',
            description='Description test',
            prix=5000,
            culture='Maïs',
            region=self.region,
            prefecture=self.prefecture,
            canton=self.canton,
            actif=True
        )
        
        # Créer une transaction
        self.transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=5000,
            statut='SUCCESS'
        )
        
        # Créer un achat
        self.achat = AchatDocument.objects.create(
            acheteur=self.user,
            document=self.document,
            transaction=self.transaction,
            lien_telechargement='test_token_123',
            expiration_lien=timezone.now() + timedelta(hours=48)
        )
        
        # Initialiser le service
        self.email_service = EmailService()
    
    def test_email_service_initialization(self):
        """Test: Initialisation du service d'email"""
        self.assertIsNotNone(self.email_service.from_email)
        self.assertEqual(
            self.email_service.frontend_url,
            'http://localhost:5173'
        )
    
    def test_send_purchase_confirmation_success(self):
        """Test: Envoi réussi d'un email de confirmation d'achat"""
        download_url = 'http://localhost:8000/api/v1/documents/1/download?token=abc123'
        
        result = self.email_service.send_purchase_confirmation(
            self.achat,
            download_url
        )
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, ['jean.dupont@example.com'])
        self.assertIn('Confirmation d\'achat', email.subject)
        self.assertIn('Document Test', email.subject)
        self.assertIn(download_url, email.body)
    
    def test_send_purchase_confirmation_no_email(self):
        """Test: Échec si l'utilisateur n'a pas d'email"""
        self.user.email = ''
        self.user.save()
        
        download_url = 'http://localhost:8000/api/v1/documents/1/download?token=abc123'
        
        result = self.email_service.send_purchase_confirmation(
            self.achat,
            download_url
        )
        
        self.assertFalse(result)
        self.assertEqual(len(mail.outbox), 0)
    
    def test_send_purchase_confirmation_invalid_email(self):
        """Test: Gestion gracieuse d'un email invalide"""
        self.user.email = 'invalid-email'
        self.user.save()
        
        download_url = 'http://localhost:8000/api/v1/documents/1/download?token=abc123'
        
        # Ne devrait pas lever d'exception
        result = self.email_service.send_purchase_confirmation(
            self.achat,
            download_url
        )
        
        # Devrait échouer mais ne pas crasher
        self.assertFalse(result)
    
    def test_send_expiration_reminder_success(self):
        """Test: Envoi réussi d'un rappel d'expiration"""
        result = self.email_service.send_expiration_reminder(
            self.achat,
            hours_remaining=24
        )
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, ['jean.dupont@example.com'])
        self.assertIn('Rappel', email.subject)
        self.assertIn('expire', email.subject.lower())
        self.assertIn('24', email.body)
    
    def test_send_expiration_reminder_already_expired(self):
        """Test: Pas d'envoi si le lien est déjà expiré"""
        # Expirer le lien
        self.achat.expiration_lien = timezone.now() - timedelta(hours=1)
        self.achat.save()
        
        result = self.email_service.send_expiration_reminder(
            self.achat,
            hours_remaining=24
        )
        
        # Ne devrait pas envoyer d'email
        self.assertFalse(result)
        self.assertEqual(len(mail.outbox), 0)
    
    def test_send_link_regenerated_success(self):
        """Test: Envoi réussi d'une confirmation de régénération"""
        download_url = 'http://localhost:8000/api/v1/documents/1/download?token=new_token'
        
        result = self.email_service.send_link_regenerated(
            self.achat,
            download_url
        )
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to, ['jean.dupont@example.com'])
        self.assertIn('Nouveau lien', email.subject)
        self.assertIn(download_url, email.body)
    
    def test_send_bulk_expiration_reminders(self):
        """Test: Envoi en masse de rappels d'expiration"""
        # Créer plusieurs achats
        achats = []
        for i in range(3):
            user = User.objects.create_user(
                phone_number=f'+2289012345{i}',
                password='testpass123',
                email=f'user{i}@example.com',
                user_type='EXPLOITANT'
            )
            
            transaction = Transaction.objects.create(
                utilisateur=user,
                type_transaction='ACHAT_DOCUMENT',
                montant=5000,
                statut='SUCCESS'
            )
            
            achat = AchatDocument.objects.create(
                acheteur=user,
                document=self.document,
                transaction=transaction,
                lien_telechargement=f'token_{i}',
                expiration_lien=timezone.now() + timedelta(hours=24)
            )
            achats.append(achat)
        
        # Envoyer en masse
        stats = self.email_service.send_bulk_expiration_reminders(
            achats,
            hours_remaining=24
        )
        
        self.assertEqual(stats['success'], 3)
        self.assertEqual(stats['failed'], 0)
        self.assertEqual(len(mail.outbox), 3)
    
    def test_send_bulk_with_failures(self):
        """Test: Envoi en masse avec quelques échecs"""
        # Créer des achats, certains sans email
        achats = []
        for i in range(3):
            user = User.objects.create_user(
                phone_number=f'+2289012346{i}',
                password='testpass123',
                email=f'user{i}@example.com' if i < 2 else '',  # Dernier sans email
                user_type='EXPLOITANT'
            )
            
            transaction = Transaction.objects.create(
                utilisateur=user,
                type_transaction='ACHAT_DOCUMENT',
                montant=5000,
                statut='SUCCESS'
            )
            
            achat = AchatDocument.objects.create(
                acheteur=user,
                document=self.document,
                transaction=transaction,
                lien_telechargement=f'token_fail_{i}',
                expiration_lien=timezone.now() + timedelta(hours=24)
            )
            achats.append(achat)
        
        # Envoyer en masse
        stats = self.email_service.send_bulk_expiration_reminders(
            achats,
            hours_remaining=24
        )
        
        self.assertEqual(stats['success'], 2)
        self.assertEqual(stats['failed'], 1)
        self.assertEqual(len(mail.outbox), 2)
    
    @patch('apps.documents.services.email_service.render_to_string')
    def test_render_email_template_error_handling(self, mock_render):
        """Test: Gestion d'erreur lors du rendu de template"""
        mock_render.side_effect = Exception('Template error')
        
        with self.assertRaises(Exception):
            self.email_service._render_email_template(
                'emails/test.html',
                {}
            )
    
    def test_email_contains_correct_context(self):
        """Test: L'email contient toutes les informations nécessaires"""
        download_url = 'http://localhost:8000/api/v1/documents/1/download?token=abc123'
        
        self.email_service.send_purchase_confirmation(
            self.achat,
            download_url
        )
        
        email = mail.outbox[0]
        
        # Vérifier que l'email contient les informations importantes
        self.assertIn('Jean', email.body)
        self.assertIn('Document Test', email.body)
        self.assertIn(download_url, email.body)
        self.assertIn('5000', email.body)  # Prix
        self.assertIn('Maïs', email.body)  # Culture
    
    def test_email_has_html_alternative(self):
        """Test: L'email a une version HTML"""
        download_url = 'http://localhost:8000/api/v1/documents/1/download?token=abc123'
        
        self.email_service.send_purchase_confirmation(
            self.achat,
            download_url
        )
        
        email = mail.outbox[0]
        
        # Vérifier qu'il y a une alternative HTML
        self.assertEqual(len(email.alternatives), 1)
        self.assertEqual(email.alternatives[0][1], 'text/html')
