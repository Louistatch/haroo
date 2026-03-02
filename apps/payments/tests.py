"""
Tests pour l'application payments
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from unittest.mock import patch, MagicMock

from .models import Transaction
from .services import FedapayService, TransactionService, CommissionCalculator

User = get_user_model()


class TransactionModelTest(TestCase):
    """Tests pour le modèle Transaction"""
    
    def setUp(self):
        """Créer un utilisateur de test"""
        self.user = User.objects.create_user(
            username='testuser',
            phone_number='+22890123456',
            password='TestPass123!',
            user_type='ACHETEUR'
        )
    
    def test_create_transaction(self):
        """Tester la création d'une transaction"""
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=Decimal('5000.00'),
            commission_plateforme=Decimal('0.00'),
            statut='PENDING'
        )
        
        self.assertEqual(transaction.utilisateur, self.user)
        self.assertEqual(transaction.type_transaction, 'ACHAT_DOCUMENT')
        self.assertEqual(transaction.montant, Decimal('5000.00'))
        self.assertEqual(transaction.statut, 'PENDING')
        self.assertIsNotNone(transaction.id)
    
    def test_transaction_str(self):
        """Tester la représentation string d'une transaction"""
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=Decimal('5000.00'),
            statut='SUCCESS'
        )
        
        expected = "Achat Document - 5000.00 FCFA (Réussie)"
        self.assertEqual(str(transaction), expected)


class TransactionServiceTest(TestCase):
    """Tests pour TransactionService"""
    
    def setUp(self):
        """Créer un utilisateur de test"""
        self.user = User.objects.create_user(
            username='testuser',
            phone_number='+22890123456',
            password='TestPass123!',
            user_type='EXPLOITANT'
        )
    
    def test_create_transaction_with_commission(self):
        """Tester la création d'une transaction avec calcul de commission"""
        transaction = TransactionService.create_transaction(
            utilisateur=self.user,
            type_transaction='RECRUTEMENT_AGRONOME',
            montant=Decimal('50000.00'),
            reference_externe='mission_123'
        )
        
        self.assertEqual(transaction.utilisateur, self.user)
        self.assertEqual(transaction.type_transaction, 'RECRUTEMENT_AGRONOME')
        self.assertEqual(transaction.montant, Decimal('50000.00'))
        self.assertEqual(transaction.commission_plateforme, Decimal('5000.00'))  # 10%
        self.assertEqual(transaction.reference_externe, 'mission_123')
        self.assertEqual(transaction.statut, 'PENDING')
    
    def test_create_transaction_no_commission(self):
        """Tester la création d'une transaction sans commission"""
        transaction = TransactionService.create_transaction(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=Decimal('3000.00')
        )
        
        self.assertEqual(transaction.commission_plateforme, Decimal('0.00'))
    
    def test_update_transaction_status(self):
        """Tester la mise à jour du statut d'une transaction"""
        transaction = TransactionService.create_transaction(
            utilisateur=self.user,
            type_transaction='PREVENTE',
            montant=Decimal('100000.00')
        )
        
        self.assertEqual(transaction.statut, 'PENDING')
        
        updated = TransactionService.update_transaction_status(
            transaction=transaction,
            new_status='SUCCESS'
        )
        
        self.assertEqual(updated.statut, 'SUCCESS')


class CommissionCalculatorTest(TestCase):
    """Tests pour CommissionCalculator"""
    
    def test_get_commission_rate_agronome(self):
        """Tester le taux de commission pour recrutement agronome"""
        rate = CommissionCalculator.get_commission_rate('RECRUTEMENT_AGRONOME')
        self.assertEqual(rate, 10)
    
    def test_get_commission_rate_prevente(self):
        """Tester le taux de commission pour prévente"""
        rate = CommissionCalculator.get_commission_rate('PREVENTE')
        self.assertEqual(rate, 5)
    
    def test_get_commission_rate_transport(self):
        """Tester le taux de commission pour transport"""
        rate = CommissionCalculator.get_commission_rate('TRANSPORT')
        self.assertEqual(rate, 8)
    
    def test_get_commission_rate_document(self):
        """Tester le taux de commission pour achat document (0%)"""
        rate = CommissionCalculator.get_commission_rate('ACHAT_DOCUMENT')
        self.assertEqual(rate, 0)
    
    def test_calculate_net_amount(self):
        """Tester le calcul du montant net"""
        montant = Decimal('50000.00')
        commission = Decimal('5000.00')
        
        net = CommissionCalculator.calculate_net_amount(montant, commission)
        
        self.assertEqual(net, Decimal('45000.00'))


class FedapayServiceTest(TestCase):
    """Tests pour FedapayService"""
    
    def setUp(self):
        """Créer un utilisateur et une transaction de test"""
        self.user = User.objects.create_user(
            username='testuser',
            phone_number='+22890123456',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            password='TestPass123!',
            user_type='ACHETEUR'
        )
        
        self.transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=Decimal('5000.00'),
            statut='PENDING'
        )
    
    @patch('apps.payments.services.fedapay')
    def test_initiate_payment_success(self, mock_fedapay):
        """Tester l'initialisation réussie d'un paiement"""
        # Mock de la réponse Fedapay
        mock_transaction_class = MagicMock()
        mock_fedapay_transaction = MagicMock()
        mock_fedapay_transaction.id = 'fedapay_123'
        mock_fedapay_transaction.generateToken.return_value = MagicMock(
            url='https://checkout.fedapay.com/test',
            token='test_token'
        )
        mock_transaction_class.create.return_value = mock_fedapay_transaction
        mock_fedapay.Transaction = mock_transaction_class
        
        # Initialiser le paiement
        service = FedapayService()
        result = service.initiate_payment(
            transaction=self.transaction,
            callback_url='https://example.com/callback',
            description='Test payment'
        )
        
        # Vérifications
        self.assertTrue(result['success'])
        self.assertEqual(result['fedapay_transaction_id'], 'fedapay_123')
        self.assertEqual(result['payment_url'], 'https://checkout.fedapay.com/test')
        self.assertEqual(result['token'], 'test_token')
        
        # Vérifier que la transaction a été mise à jour
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.fedapay_transaction_id, 'fedapay_123')
    
    @patch('apps.payments.services.fedapay')
    def test_initiate_payment_failure(self, mock_fedapay):
        """Tester l'échec de l'initialisation d'un paiement"""
        # Mock d'une erreur Fedapay
        mock_transaction_class = MagicMock()
        mock_transaction_class.create.side_effect = Exception('Fedapay API error')
        mock_fedapay.Transaction = mock_transaction_class
        
        # Initialiser le paiement
        service = FedapayService()
        
        with self.assertRaises(Exception) as context:
            service.initiate_payment(
                transaction=self.transaction,
                callback_url='https://example.com/callback'
            )
        
        self.assertIn('Échec de l\'initialisation du paiement', str(context.exception))
        
        # Vérifier que la transaction a été marquée comme échouée
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.statut, 'FAILED')
    
    def test_verify_webhook_signature(self):
        """Tester la vérification de signature webhook"""
        service = FedapayService()
        
        # Note: Ce test nécessiterait une vraie clé secrète et signature
        # Pour l'instant, on teste juste que la méthode ne plante pas
        payload = '{"event": "transaction.approved"}'
        signature = 'test_signature'
        
        # La signature sera invalide mais ne devrait pas planter
        result = service.verify_webhook_signature(payload, signature)
        self.assertIsInstance(result, bool)



class WebhookViewTest(TestCase):
    """Tests pour le endpoint webhook Fedapay"""
    
    def setUp(self):
        """Créer un utilisateur et une transaction de test"""
        self.user = User.objects.create_user(
            username='testuser',
            phone_number='+22890123456',
            email='test@example.com',
            password='TestPass123!',
            user_type='ACHETEUR'
        )
        
        self.transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=Decimal('5000.00'),
            statut='PENDING',
            fedapay_transaction_id='fedapay_123'
        )
    
    @patch('apps.payments.views.FedapayService.verify_webhook_signature')
    @patch('apps.payments.views.PostPaymentActionHandler.handle_successful_payment')
    def test_webhook_transaction_approved(self, mock_handler, mock_verify):
        """Tester le webhook pour une transaction approuvée"""
        mock_verify.return_value = True
        mock_handler.return_value = True
        
        payload = {
            "event": "transaction.approved",
            "entity": {
                "id": "fedapay_123",
                "status": "approved",
                "amount": 5000
            }
        }
        
        response = self.client.post(
            '/api/v1/payments/webhooks/fedapay',
            data=payload,
            content_type='application/json',
            HTTP_X_FEDAPAY_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Vérifier que la transaction a été mise à jour
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.statut, 'SUCCESS')
        
        # Vérifier que le handler a été appelé
        mock_handler.assert_called_once_with(self.transaction)
    
    @patch('apps.payments.views.FedapayService.verify_webhook_signature')
    def test_webhook_transaction_failed(self, mock_verify):
        """Tester le webhook pour une transaction échouée"""
        mock_verify.return_value = True
        
        payload = {
            "event": "transaction.failed",
            "entity": {
                "id": "fedapay_123",
                "status": "failed",
                "amount": 5000
            }
        }
        
        response = self.client.post(
            '/api/v1/payments/webhooks/fedapay',
            data=payload,
            content_type='application/json',
            HTTP_X_FEDAPAY_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la transaction a été mise à jour
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.statut, 'FAILED')
    
    @patch('apps.payments.views.FedapayService.verify_webhook_signature')
    def test_webhook_invalid_signature(self, mock_verify):
        """Tester le webhook avec une signature invalide"""
        mock_verify.return_value = False
        
        payload = {
            "event": "transaction.approved",
            "entity": {
                "id": "fedapay_123",
                "status": "approved"
            }
        }
        
        response = self.client.post(
            '/api/v1/payments/webhooks/fedapay',
            data=payload,
            content_type='application/json',
            HTTP_X_FEDAPAY_SIGNATURE='invalid_signature'
        )
        
        self.assertEqual(response.status_code, 401)
        
        # Vérifier que la transaction n'a pas été mise à jour
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.statut, 'PENDING')
    
    @patch('apps.payments.views.FedapayService.verify_webhook_signature')
    def test_webhook_transaction_not_found(self, mock_verify):
        """Tester le webhook pour une transaction inexistante"""
        mock_verify.return_value = True
        
        payload = {
            "event": "transaction.approved",
            "entity": {
                "id": "nonexistent_id",
                "status": "approved"
            }
        }
        
        response = self.client.post(
            '/api/v1/payments/webhooks/fedapay',
            data=payload,
            content_type='application/json',
            HTTP_X_FEDAPAY_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response.status_code, 404)
    
    @patch('apps.payments.views.FedapayService.verify_webhook_signature')
    def test_webhook_idempotence(self, mock_verify):
        """Tester l'idempotence des webhooks (même transaction_id = même résultat)"""
        mock_verify.return_value = True
        
        payload = {
            "event": "transaction.approved",
            "entity": {
                "id": "fedapay_123",
                "status": "approved",
                "amount": 5000
            }
        }
        
        # Premier appel
        response1 = self.client.post(
            '/api/v1/payments/webhooks/fedapay',
            data=payload,
            content_type='application/json',
            HTTP_X_FEDAPAY_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response1.status_code, 200)
        self.transaction.refresh_from_db()
        first_updated_at = self.transaction.updated_at
        
        # Deuxième appel avec le même payload
        response2 = self.client.post(
            '/api/v1/payments/webhooks/fedapay',
            data=payload,
            content_type='application/json',
            HTTP_X_FEDAPAY_SIGNATURE='test_signature'
        )
        
        self.assertEqual(response2.status_code, 200)
        self.transaction.refresh_from_db()
        
        # Le statut devrait rester SUCCESS
        self.assertEqual(self.transaction.statut, 'SUCCESS')


class PostPaymentActionHandlerTest(TestCase):
    """Tests pour PostPaymentActionHandler"""
    
    def setUp(self):
        """Créer les données de test"""
        from apps.locations.models import Region, Prefecture, Canton
        from apps.documents.models import DocumentTechnique, DocumentTemplate
        
        self.user = User.objects.create_user(
            username='testuser',
            phone_number='+22890123456',
            email='test@example.com',
            password='TestPass123!',
            user_type='ACHETEUR'
        )
        
        # Créer les données géographiques
        self.region = Region.objects.create(nom='Maritime', code='MAR')
        self.prefecture = Prefecture.objects.create(
            nom='Golfe',
            code='GOL',
            region=self.region
        )
        self.canton = Canton.objects.create(
            nom='Lomé',
            code='LOM',
            prefecture=self.prefecture
        )
        
        # Créer un template et un document
        self.template = DocumentTemplate.objects.create(
            titre='Template Test',
            description='Description test',
            type_document='COMPTE_EXPLOITATION',
            format_fichier='EXCEL',
            fichier_template='templates/test.xlsx'
        )
        
        self.document = DocumentTechnique.objects.create(
            template=self.template,
            titre='Document Test',
            description='Description test',
            prix=Decimal('5000.00'),
            canton=self.canton,
            culture='Maïs',
            fichier_genere='documents/test.xlsx'
        )
    
    def test_handle_document_purchase_success(self):
        """Tester le déblocage d'un document après paiement réussi"""
        from apps.payments.post_payment_actions import PostPaymentActionHandler
        from apps.documents.models import AchatDocument
        
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=Decimal('5000.00'),
            statut='SUCCESS',
            reference_externe=str(self.document.id)
        )
        
        # Exécuter l'action post-paiement
        success = PostPaymentActionHandler.handle_successful_payment(transaction)
        
        self.assertTrue(success)
        
        # Vérifier que l'achat a été créé
        achat = AchatDocument.objects.get(transaction=transaction)
        self.assertEqual(achat.acheteur, self.user)
        self.assertEqual(achat.document, self.document)
        self.assertIsNotNone(achat.lien_telechargement)
        self.assertIsNotNone(achat.expiration_lien)
        self.assertEqual(achat.nombre_telechargements, 0)
    
    def test_handle_document_purchase_idempotence(self):
        """Tester l'idempotence du déblocage de document"""
        from apps.payments.post_payment_actions import PostPaymentActionHandler
        from apps.documents.models import AchatDocument
        
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=Decimal('5000.00'),
            statut='SUCCESS',
            reference_externe=str(self.document.id)
        )
        
        # Premier appel
        success1 = PostPaymentActionHandler.handle_successful_payment(transaction)
        self.assertTrue(success1)
        
        # Deuxième appel
        success2 = PostPaymentActionHandler.handle_successful_payment(transaction)
        self.assertTrue(success2)
        
        # Vérifier qu'il n'y a qu'un seul achat
        achats = AchatDocument.objects.filter(transaction=transaction)
        self.assertEqual(achats.count(), 1)
    
    def test_handle_document_purchase_missing_reference(self):
        """Tester le déblocage avec référence externe manquante"""
        from apps.payments.post_payment_actions import PostPaymentActionHandler
        
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=Decimal('5000.00'),
            statut='SUCCESS',
            reference_externe=None  # Pas de référence
        )
        
        # Exécuter l'action post-paiement
        success = PostPaymentActionHandler.handle_successful_payment(transaction)
        
        self.assertFalse(success)
    
    def test_handle_document_purchase_document_not_found(self):
        """Tester le déblocage avec document inexistant"""
        from apps.payments.post_payment_actions import PostPaymentActionHandler
        
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=Decimal('5000.00'),
            statut='SUCCESS',
            reference_externe='99999'  # ID inexistant
        )
        
        # Exécuter l'action post-paiement
        success = PostPaymentActionHandler.handle_successful_payment(transaction)
        
        self.assertFalse(success)
    
    def test_handle_non_success_transaction(self):
        """Tester qu'aucune action n'est exécutée pour une transaction non réussie"""
        from apps.payments.post_payment_actions import PostPaymentActionHandler
        
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=Decimal('5000.00'),
            statut='PENDING',  # Pas SUCCESS
            reference_externe=str(self.document.id)
        )
        
        # Exécuter l'action post-paiement
        success = PostPaymentActionHandler.handle_successful_payment(transaction)
        
        self.assertFalse(success)
    
    def test_handle_agronomist_recruitment(self):
        """Tester le handler pour recrutement d'agronome"""
        from apps.payments.post_payment_actions import PostPaymentActionHandler
        
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='RECRUTEMENT_AGRONOME',
            montant=Decimal('50000.00'),
            statut='SUCCESS',
            reference_externe='mission_123'
        )
        
        # Exécuter l'action post-paiement
        success = PostPaymentActionHandler.handle_successful_payment(transaction)
        
        # Pour l'instant, le handler retourne True (TODO implémenté)
        self.assertTrue(success)
    
    def test_handle_presale(self):
        """Tester le handler pour prévente"""
        from apps.payments.post_payment_actions import PostPaymentActionHandler
        
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='PREVENTE',
            montant=Decimal('100000.00'),
            statut='SUCCESS',
            reference_externe='prevente_123'
        )
        
        # Exécuter l'action post-paiement
        success = PostPaymentActionHandler.handle_successful_payment(transaction)
        
        # Pour l'instant, le handler retourne True (TODO implémenté)
        self.assertTrue(success)
