"""
Tests pour le système d'escrow (séquestre de paiements)
"""
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import timedelta

from apps.payments.models import Transaction, EscrowAccount
from apps.payments.services import EscrowService, CommissionCalculator
from apps.locations.models import Region, Prefecture, Canton
from apps.users.models import ExploitantProfile, AgronomeProfile
from apps.missions.models import Mission

User = get_user_model()


class EscrowServiceTest(TestCase):
    """Tests pour le service d'escrow"""
    
    def setUp(self):
        """Préparer les données de test"""
        # Créer les données géographiques
        self.region = Region.objects.create(nom="Maritime", code="MAR")
        self.prefecture = Prefecture.objects.create(
            nom="Golfe",
            code="GOL",
            region=self.region
        )
        self.canton = Canton.objects.create(
            nom="Lomé 1er",
            code="LOM1",
            prefecture=self.prefecture
        )
        
        # Créer un exploitant vérifié
        self.exploitant = User.objects.create_user(
            username="exploitant",
            phone_number="+22890123456",
            password="password123",
            user_type="EXPLOITANT"
        )
        self.exploitant_profile = ExploitantProfile.objects.create(
            user=self.exploitant,
            superficie_totale=Decimal("15.00"),
            canton_principal=self.canton,
            coordonnees_gps='{"type": "Point", "coordinates": [1.2, 6.1]}',
            statut_verification="VERIFIE"
        )
        
        # Créer un agronome validé
        self.agronome = User.objects.create_user(
            username="agronome",
            phone_number="+22890123457",
            password="password123",
            user_type="AGRONOME"
        )
        self.agronome_profile = AgronomeProfile.objects.create(
            user=self.agronome,
            canton_rattachement=self.canton,
            specialisations=["Maraîchage", "Irrigation"],
            statut_validation="VALIDE",
            badge_valide=True
        )
        
        # Créer une transaction
        self.transaction = Transaction.objects.create(
            utilisateur=self.exploitant,
            type_transaction="RECRUTEMENT_AGRONOME",
            montant=Decimal("50000.00"),
            commission_plateforme=Decimal("5000.00"),  # 10%
            statut="SUCCESS"
        )
    
    def test_create_escrow(self):
        """Test de création d'un compte escrow"""
        date_liberation = timezone.now() + timedelta(days=30)
        
        escrow = EscrowService.create_escrow(
            transaction=self.transaction,
            beneficiaire=self.agronome,
            montant_bloque=Decimal("50000.00"),
            date_liberation_prevue=date_liberation
        )
        
        self.assertIsNotNone(escrow)
        self.assertEqual(escrow.transaction, self.transaction)
        self.assertEqual(escrow.beneficiaire, self.agronome)
        self.assertEqual(escrow.montant_bloque, Decimal("50000.00"))
        self.assertEqual(escrow.statut, "BLOQUE")
        self.assertEqual(escrow.date_liberation_prevue, date_liberation)
        self.assertIsNone(escrow.date_liberation_effective)
    
    def test_release_escrow(self):
        """Test de libération d'un paiement en escrow"""
        # Créer un escrow
        date_liberation = timezone.now() + timedelta(days=30)
        escrow = EscrowService.create_escrow(
            transaction=self.transaction,
            beneficiaire=self.agronome,
            montant_bloque=Decimal("50000.00"),
            date_liberation_prevue=date_liberation
        )
        
        # Libérer l'escrow
        result = EscrowService.release_escrow(escrow.id)
        
        # Vérifier le résultat
        self.assertTrue(result['success'])
        self.assertEqual(result['montant_brut'], 50000.00)
        self.assertEqual(result['commission'], 5000.00)
        self.assertEqual(result['montant_net'], 45000.00)
        self.assertEqual(result['beneficiaire_id'], self.agronome.id)
        
        # Vérifier que l'escrow a été mis à jour
        escrow.refresh_from_db()
        self.assertEqual(escrow.statut, "LIBERE")
        self.assertIsNotNone(escrow.date_liberation_effective)
    
    def test_release_escrow_already_released(self):
        """Test de libération d'un escrow déjà libéré"""
        # Créer et libérer un escrow
        date_liberation = timezone.now() + timedelta(days=30)
        escrow = EscrowService.create_escrow(
            transaction=self.transaction,
            beneficiaire=self.agronome,
            montant_bloque=Decimal("50000.00"),
            date_liberation_prevue=date_liberation
        )
        EscrowService.release_escrow(escrow.id)
        
        # Tenter de libérer à nouveau
        with self.assertRaises(ValueError) as context:
            EscrowService.release_escrow(escrow.id)
        
        self.assertIn("n'est pas en statut BLOQUE", str(context.exception))
    
    def test_refund_escrow(self):
        """Test de remboursement d'un paiement en escrow"""
        # Créer un escrow
        date_liberation = timezone.now() + timedelta(days=30)
        escrow = EscrowService.create_escrow(
            transaction=self.transaction,
            beneficiaire=self.agronome,
            montant_bloque=Decimal("50000.00"),
            date_liberation_prevue=date_liberation
        )
        
        # Rembourser l'escrow
        result = EscrowService.refund_escrow(escrow.id, raison="Mission annulée")
        
        # Vérifier le résultat
        self.assertTrue(result['success'])
        self.assertEqual(result['montant_rembourse'], 50000.00)
        self.assertEqual(result['payeur_id'], self.exploitant.id)
        self.assertEqual(result['raison'], "Mission annulée")
        
        # Vérifier que l'escrow a été mis à jour
        escrow.refresh_from_db()
        self.assertEqual(escrow.statut, "REMBOURSE")
        self.assertIsNotNone(escrow.date_liberation_effective)
        
        # Vérifier que la transaction a été remboursée
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.statut, "REFUNDED")
    
    def test_get_escrow_by_transaction(self):
        """Test de récupération d'un escrow par transaction"""
        # Créer un escrow
        date_liberation = timezone.now() + timedelta(days=30)
        escrow = EscrowService.create_escrow(
            transaction=self.transaction,
            beneficiaire=self.agronome,
            montant_bloque=Decimal("50000.00"),
            date_liberation_prevue=date_liberation
        )
        
        # Récupérer l'escrow
        found_escrow = EscrowService.get_escrow_by_transaction(str(self.transaction.id))
        
        self.assertIsNotNone(found_escrow)
        self.assertEqual(found_escrow.id, escrow.id)
    
    def test_get_escrow_by_transaction_not_found(self):
        """Test de récupération d'un escrow inexistant"""
        import uuid
        nonexistent_id = str(uuid.uuid4())
        found_escrow = EscrowService.get_escrow_by_transaction(nonexistent_id)
        self.assertIsNone(found_escrow)


class CommissionCalculatorTest(TestCase):
    """Tests pour le calculateur de commissions"""
    
    def test_calculate_net_amount(self):
        """Test de calcul du montant net après commission"""
        montant_brut = Decimal("50000.00")
        commission = Decimal("5000.00")
        
        montant_net = CommissionCalculator.calculate_net_amount(montant_brut, commission)
        
        self.assertEqual(montant_net, Decimal("45000.00"))
    
    def test_calculate_net_amount_rounding(self):
        """Test de l'arrondi du montant net"""
        montant_brut = Decimal("50000.00")
        commission = Decimal("5000.333")
        
        montant_net = CommissionCalculator.calculate_net_amount(montant_brut, commission)
        
        # Doit être arrondi à 2 décimales
        self.assertEqual(montant_net, Decimal("44999.67"))


class EscrowAccountModelTest(TestCase):
    """Tests pour le modèle EscrowAccount"""
    
    def setUp(self):
        """Préparer les données de test"""
        self.user = User.objects.create_user(
            username="testuser",
            phone_number="+22890123456",
            password="password123"
        )
        
        self.transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction="RECRUTEMENT_AGRONOME",
            montant=Decimal("50000.00"),
            commission_plateforme=Decimal("5000.00"),
            statut="SUCCESS"
        )
    
    def test_create_escrow_account(self):
        """Test de création d'un compte escrow"""
        date_liberation = timezone.now() + timedelta(days=30)
        
        escrow = EscrowAccount.objects.create(
            transaction=self.transaction,
            montant_bloque=Decimal("50000.00"),
            beneficiaire=self.user,
            statut="BLOQUE",
            date_liberation_prevue=date_liberation
        )
        
        self.assertIsNotNone(escrow.id)
        self.assertEqual(str(escrow), f"Escrow #{escrow.id} - 50000.00 FCFA (Bloqué)")
    
    def test_escrow_account_ordering(self):
        """Test de l'ordre des comptes escrow"""
        date_liberation = timezone.now() + timedelta(days=30)
        
        # Créer plusieurs escrows
        escrow1 = EscrowAccount.objects.create(
            transaction=self.transaction,
            montant_bloque=Decimal("50000.00"),
            beneficiaire=self.user,
            statut="BLOQUE",
            date_liberation_prevue=date_liberation
        )
        
        # Créer une deuxième transaction pour le deuxième escrow
        transaction2 = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction="RECRUTEMENT_AGRONOME",
            montant=Decimal("30000.00"),
            commission_plateforme=Decimal("3000.00"),
            statut="SUCCESS"
        )
        
        escrow2 = EscrowAccount.objects.create(
            transaction=transaction2,
            montant_bloque=Decimal("30000.00"),
            beneficiaire=self.user,
            statut="BLOQUE",
            date_liberation_prevue=date_liberation
        )
        
        # Vérifier l'ordre (plus récent en premier)
        escrows = list(EscrowAccount.objects.all())
        self.assertEqual(escrows[0].id, escrow2.id)
        self.assertEqual(escrows[1].id, escrow1.id)
