"""
Tests pour le module de conformité réglementaire
Exigences: 45.1, 45.2, 45.3, 45.4, 45.5, 45.6, 33.6
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from apps.payments.models import Transaction
from apps.locations.models import Region, Prefecture, Canton
from .models import (
    CGUAcceptance,
    ElectronicReceipt,
    DataRetentionPolicy,
    AccountDeletionRequest
)
from .services import (
    CGUService,
    ReceiptService,
    DataExportService,
    AccountDeletionService,
    DataRetentionService
)

User = get_user_model()


class CGUServiceTestCase(TestCase):
    """Tests pour le service CGU - Exigence 45.3"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone_number='+22890123456',
            user_type='ACHETEUR'
        )
    
    def test_record_acceptance(self):
        """Test l'enregistrement d'une acceptation CGU"""
        acceptance = CGUService.record_acceptance(
            user=self.user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )
        
        self.assertIsNotNone(acceptance)
        self.assertEqual(acceptance.user, self.user)
        self.assertEqual(acceptance.version_cgu, CGUService.CURRENT_CGU_VERSION)
        self.assertEqual(acceptance.ip_address, '192.168.1.1')
    
    def test_has_accepted_current_version(self):
        """Test la vérification de l'acceptation de la version actuelle"""
        # Avant acceptation
        self.assertFalse(CGUService.has_accepted_current_version(self.user))
        
        # Après acceptation
        CGUService.record_acceptance(
            user=self.user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )
        self.assertTrue(CGUService.has_accepted_current_version(self.user))


class ReceiptServiceTestCase(TestCase):
    """Tests pour le service de reçus - Exigence 45.5"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone_number='+22890123456',
            user_type='ACHETEUR'
        )
        
        self.transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=Decimal('10000.00'),
            statut='SUCCESS'
        )
    
    def test_generate_receipt_number(self):
        """Test la génération de numéro de reçu unique"""
        number1 = ReceiptService.generate_receipt_number()
        self.assertTrue(number1.startswith('REC-'))
        
        # Le numéro devrait contenir l'année et un compteur
        import datetime
        year = datetime.datetime.now().year
        self.assertIn(str(year), number1)
    
    def test_create_receipt(self):
        """Test la création d'un reçu électronique"""
        receipt = ReceiptService.create_receipt(self.transaction)
        
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt.transaction, self.transaction)
        self.assertEqual(receipt.buyer_name, self.user.username)
        self.assertEqual(receipt.amount, Decimal('10000.00'))
        # TVA 18%
        self.assertEqual(receipt.tax_amount, Decimal('1800.00'))
        self.assertEqual(receipt.total_amount, Decimal('11800.00'))
    
    def test_receipt_not_duplicated(self):
        """Test qu'un reçu n'est pas dupliqué"""
        receipt1 = ReceiptService.create_receipt(self.transaction)
        receipt2 = ReceiptService.create_receipt(self.transaction)
        
        self.assertEqual(receipt1.id, receipt2.id)


class DataExportServiceTestCase(TestCase):
    """Tests pour l'export de données - Exigence 33.6"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone_number='+22890123456',
            user_type='ACHETEUR',
            first_name='Test',
            last_name='User'
        )
    
    def test_export_user_data(self):
        """Test l'export des données personnelles"""
        import json
        
        data_json = DataExportService.export_user_data(self.user)
        data = json.loads(data_json)
        
        self.assertIn('user_info', data)
        self.assertIn('profile', data)
        self.assertIn('transactions', data)
        self.assertIn('cgu_acceptances', data)
        self.assertIn('export_date', data)
        
        self.assertEqual(data['user_info']['username'], 'testuser')
        self.assertEqual(data['user_info']['email'], 'test@example.com')


class AccountDeletionServiceTestCase(TestCase):
    """Tests pour la suppression de compte - Exigence 45.4"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone_number='+22890123456',
            user_type='ACHETEUR'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            phone_number='+22890123457',
            user_type='ADMIN',
            is_staff=True
        )
    
    def test_request_deletion(self):
        """Test la création d'une demande de suppression"""
        request = AccountDeletionService.request_deletion(
            user=self.user,
            reason='Test de suppression'
        )
        
        self.assertIsNotNone(request)
        self.assertEqual(request.user, self.user)
        self.assertEqual(request.status, 'PENDING')
        self.assertTrue(request.data_export_file)
    
    def test_process_deletion(self):
        """Test le traitement d'une demande de suppression"""
        deletion_request = AccountDeletionService.request_deletion(
            user=self.user,
            reason='Test'
        )
        
        processed = AccountDeletionService.process_deletion(
            deletion_request=deletion_request,
            admin_user=self.admin
        )
        
        self.assertEqual(processed.status, 'COMPLETED')
        self.assertIsNotNone(processed.processed_at)
        self.assertEqual(processed.processed_by, self.admin)
        
        # Vérifier l'anonymisation
        self.user.refresh_from_db()
        self.assertTrue(self.user.username.startswith('deleted_user_'))
        self.assertFalse(self.user.is_active)


class DataRetentionServiceTestCase(TestCase):
    """Tests pour la rétention des données - Exigence 45.6"""
    
    def test_initialize_policies(self):
        """Test l'initialisation des politiques de rétention"""
        DataRetentionService.initialize_policies()
        
        # Vérifier que les 4 politiques sont créées
        self.assertEqual(DataRetentionPolicy.objects.count(), 4)
        
        # Vérifier la politique de transaction (10 ans)
        transaction_policy = DataRetentionPolicy.objects.get(data_type='TRANSACTION')
        self.assertEqual(transaction_policy.retention_period_days, 3650)
        self.assertTrue(transaction_policy.is_active)
    
    def test_get_retention_period(self):
        """Test la récupération de la période de rétention"""
        DataRetentionService.initialize_policies()
        
        period = DataRetentionService.get_retention_period('TRANSACTION')
        self.assertEqual(period, 3650)
    
    def test_should_retain_transaction(self):
        """Test la vérification de rétention des transactions"""
        DataRetentionService.initialize_policies()
        
        # Transaction récente - doit être conservée
        recent_date = timezone.now()
        self.assertTrue(DataRetentionService.should_retain_transaction(recent_date))
        
        # Transaction de plus de 10 ans - ne doit pas être conservée
        from datetime import timedelta
        old_date = timezone.now() - timedelta(days=3651)
        self.assertFalse(DataRetentionService.should_retain_transaction(old_date))
