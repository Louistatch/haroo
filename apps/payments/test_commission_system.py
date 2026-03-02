"""
Tests pour le système de calcul des commissions et l'historique des transactions
Valide les exigences 4.5, 43.1, 43.2
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from .models import Transaction
from .services import CommissionCalculator, TransactionService

User = get_user_model()


class CommissionSystemTest(TestCase):
    """
    Tests pour le système complet de calcul des commissions
    """
    
    def setUp(self):
        """Créer un utilisateur de test"""
        self.user = User.objects.create_user(
            username='testuser',
            phone_number='+22890123456',
            email='test@example.com',
            password='TestPass123!',
            user_type='EXPLOITANT'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_commission_calculation_for_agronome_recruitment(self):
        """
        Tester que la commission de 10% est correctement calculée
        pour le recrutement d'agronome
        Valide: Exigence 43.1
        """
        montant = Decimal('50000.00')
        transaction = TransactionService.create_transaction(
            utilisateur=self.user,
            type_transaction='RECRUTEMENT_AGRONOME',
            montant=montant,
            reference_externe='mission_123'
        )
        
        # Vérifier que la commission est de 10%
        expected_commission = Decimal('5000.00')
        self.assertEqual(transaction.commission_plateforme, expected_commission)
        self.assertEqual(transaction.montant, montant)
    
    def test_commission_calculation_for_presale(self):
        """
        Tester que la commission de 5% est correctement calculée
        pour les préventes agricoles
        Valide: Exigence 43.1
        """
        montant = Decimal('100000.00')
        transaction = TransactionService.create_transaction(
            utilisateur=self.user,
            type_transaction='PREVENTE',
            montant=montant,
            reference_externe='prevente_456'
        )
        
        # Vérifier que la commission est de 5%
        expected_commission = Decimal('5000.00')
        self.assertEqual(transaction.commission_plateforme, expected_commission)
    
    def test_commission_calculation_for_transport(self):
        """
        Tester que la commission de 8% est correctement calculée
        pour le transport
        Valide: Exigence 43.1
        """
        montant = Decimal('25000.00')
        transaction = TransactionService.create_transaction(
            utilisateur=self.user,
            type_transaction='TRANSPORT',
            montant=montant,
            reference_externe='transport_789'
        )
        
        # Vérifier que la commission est de 8%
        expected_commission = Decimal('2000.00')
        self.assertEqual(transaction.commission_plateforme, expected_commission)
    
    def test_no_commission_for_document_purchase(self):
        """
        Tester qu'il n'y a pas de commission pour l'achat de documents
        Valide: Exigence 43.1
        """
        montant = Decimal('5000.00')
        transaction = TransactionService.create_transaction(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=montant,
            reference_externe='doc_123'
        )
        
        # Vérifier qu'il n'y a pas de commission
        self.assertEqual(transaction.commission_plateforme, Decimal('0.00'))
    
    def test_commission_recorded_in_transaction(self):
        """
        Tester que la commission est enregistrée dans chaque transaction
        Valide: Exigence 43.2
        """
        # Créer plusieurs transactions avec différents types
        transactions_data = [
            ('RECRUTEMENT_AGRONOME', Decimal('50000.00'), Decimal('5000.00')),
            ('PREVENTE', Decimal('100000.00'), Decimal('5000.00')),
            ('TRANSPORT', Decimal('25000.00'), Decimal('2000.00')),
            ('ACHAT_DOCUMENT', Decimal('5000.00'), Decimal('0.00')),
        ]
        
        for type_trans, montant, expected_commission in transactions_data:
            transaction = TransactionService.create_transaction(
                utilisateur=self.user,
                type_transaction=type_trans,
                montant=montant
            )
            
            # Vérifier que la commission est enregistrée
            self.assertIsNotNone(transaction.commission_plateforme)
            self.assertEqual(transaction.commission_plateforme, expected_commission)
            
            # Vérifier que la transaction est sauvegardée en base
            saved_transaction = Transaction.objects.get(id=transaction.id)
            self.assertEqual(saved_transaction.commission_plateforme, expected_commission)
    
    def test_commission_calculator_get_rate(self):
        """
        Tester que CommissionCalculator retourne les bons taux
        Valide: Exigence 43.1
        """
        # Tester tous les types de transactions
        self.assertEqual(
            CommissionCalculator.get_commission_rate('RECRUTEMENT_AGRONOME'),
            10
        )
        self.assertEqual(
            CommissionCalculator.get_commission_rate('PREVENTE'),
            5
        )
        self.assertEqual(
            CommissionCalculator.get_commission_rate('TRANSPORT'),
            8
        )
        self.assertEqual(
            CommissionCalculator.get_commission_rate('ACHAT_DOCUMENT'),
            0
        )
        self.assertEqual(
            CommissionCalculator.get_commission_rate('ABONNEMENT'),
            0
        )
    
    def test_commission_calculator_net_amount(self):
        """
        Tester le calcul du montant net après commission
        """
        montant = Decimal('50000.00')
        commission = Decimal('5000.00')
        
        net_amount = CommissionCalculator.calculate_net_amount(montant, commission)
        
        self.assertEqual(net_amount, Decimal('45000.00'))
    
    def test_commission_precision(self):
        """
        Tester que les commissions sont calculées avec 2 décimales
        """
        # Montant qui donnera une commission avec plusieurs décimales
        montant = Decimal('12345.67')
        transaction = TransactionService.create_transaction(
            utilisateur=self.user,
            type_transaction='RECRUTEMENT_AGRONOME',
            montant=montant
        )
        
        # Vérifier que la commission a exactement 2 décimales
        commission_str = str(transaction.commission_plateforme)
        decimal_part = commission_str.split('.')[1] if '.' in commission_str else ''
        self.assertLessEqual(len(decimal_part), 2)


class TransactionHistoryAPITest(TestCase):
    """
    Tests pour l'endpoint GET /api/v1/transactions/history
    """
    
    def setUp(self):
        """Créer des utilisateurs et transactions de test"""
        self.user1 = User.objects.create_user(
            username='user1',
            phone_number='+22890111111',
            email='user1@example.com',
            password='TestPass123!',
            user_type='EXPLOITANT'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            phone_number='+22890222222',
            email='user2@example.com',
            password='TestPass123!',
            user_type='AGRONOME'
        )
        
        # Créer des transactions pour user1
        self.trans1 = TransactionService.create_transaction(
            utilisateur=self.user1,
            type_transaction='RECRUTEMENT_AGRONOME',
            montant=Decimal('50000.00'),
            reference_externe='mission_1'
        )
        self.trans2 = TransactionService.create_transaction(
            utilisateur=self.user1,
            type_transaction='PREVENTE',
            montant=Decimal('100000.00'),
            reference_externe='prevente_1'
        )
        
        # Créer une transaction pour user2
        self.trans3 = TransactionService.create_transaction(
            utilisateur=self.user2,
            type_transaction='TRANSPORT',
            montant=Decimal('25000.00')
        )
        
        self.client = APIClient()
    
    def test_transaction_history_endpoint_exists(self):
        """
        Tester que l'endpoint GET /api/v1/transactions/history existe
        Valide: Exigence 43.2
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/payments/transactions/history')
        
        # L'endpoint doit exister (pas 404)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_transaction_history_requires_authentication(self):
        """
        Tester que l'endpoint nécessite une authentification
        """
        response = self.client.get('/api/v1/payments/transactions/history')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_transaction_history_returns_user_transactions(self):
        """
        Tester que l'endpoint retourne uniquement les transactions de l'utilisateur
        Valide: Exigence 43.2
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/payments/transactions/history')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # L'API peut retourner une liste paginée ou directe
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        
        self.assertEqual(len(results), 2)  # user1 a 2 transactions
        
        # Vérifier que les IDs correspondent
        transaction_ids = [str(t['id']) for t in results]
        self.assertIn(str(self.trans1.id), transaction_ids)
        self.assertIn(str(self.trans2.id), transaction_ids)
        self.assertNotIn(str(self.trans3.id), transaction_ids)  # trans3 appartient à user2
    
    def test_transaction_history_includes_commission(self):
        """
        Tester que l'historique inclut les informations de commission
        Valide: Exigence 43.2
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/payments/transactions/history')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # L'API peut retourner une liste paginée ou directe
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        
        # Vérifier que chaque transaction contient la commission
        for transaction in results:
            self.assertIn('commission_plateforme', transaction)
            self.assertIsNotNone(transaction['commission_plateforme'])
    
    def test_transaction_history_filter_by_type(self):
        """
        Tester le filtrage par type de transaction
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(
            '/api/v1/payments/transactions/history?type=RECRUTEMENT_AGRONOME'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # L'API peut retourner une liste paginée ou directe
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['type_transaction'], 'RECRUTEMENT_AGRONOME')
    
    def test_transaction_history_filter_by_status(self):
        """
        Tester le filtrage par statut de transaction
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(
            '/api/v1/payments/transactions/history?statut=PENDING'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # L'API peut retourner une liste paginée ou directe
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        
        # Toutes les transactions créées sont en PENDING
        self.assertEqual(len(results), 2)
    
    def test_transaction_history_ordered_by_date(self):
        """
        Tester que les transactions sont triées par date décroissante
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/payments/transactions/history')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # L'API peut retourner une liste paginée ou directe
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        
        # Vérifier l'ordre (la plus récente en premier)
        if len(results) >= 2:
            first_date = results[0]['created_at']
            second_date = results[1]['created_at']
            self.assertGreaterEqual(first_date, second_date)
    
    def test_transaction_history_response_format(self):
        """
        Tester le format de la réponse de l'historique
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/payments/transactions/history')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # L'API peut retourner une liste paginée ou directe
        results = response.data.get('results', response.data) if isinstance(response.data, dict) else response.data
        
        # Vérifier les champs requis dans la réponse
        required_fields = [
            'id',
            'type_transaction',
            'type_transaction_display',
            'montant',
            'commission_plateforme',
            'statut',
            'statut_display',
            'created_at'
        ]
        
        for transaction in results:
            for field in required_fields:
                self.assertIn(field, transaction)
