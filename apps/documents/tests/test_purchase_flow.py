"""
Tests pour le flux d'achat de documents
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from apps.users.models import User
from apps.locations.models import Region, Prefecture, Canton
from apps.documents.models import (
    DocumentTemplate,
    DocumentTechnique,
    AchatDocument,
    DownloadLog
)
from apps.payments.models import Transaction
from apps.documents.services.secure_download import SecureDownloadService


class PurchaseFlowTestCase(TestCase):
    """
    Tests pour le flux d'achat de documents
    
    Exigences: 3.4, 4.1, 5.1, 5.2, 5.5
    """
    
    def setUp(self):
        """Configuration initiale des tests"""
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            phone_number='+22890123456',
            password='testpass123',
            user_type='ACHETEUR'
        )
        
        # Créer la hiérarchie administrative
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
        
        # Créer un template
        self.template = DocumentTemplate.objects.create(
            titre='Template Test',
            description='Template de test',
            type_document='ITINERAIRE_TECHNIQUE',  # Changed from COMPTE_EXPLOITATION
            format_fichier='EXCEL',
            variables_requises=['canton', 'culture', 'prix']
        )
        
        # Créer un document
        self.document = DocumentTechnique.objects.create(
            template=self.template,
            titre='Document Test Maïs',
            description='Document de test',
            prix=Decimal('5000.00'),
            region=self.region,
            prefecture=self.prefecture,
            canton=self.canton,
            culture='Maïs',
            actif=True
        )
        
        # Client API
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_purchase_document_creates_transaction(self):
        """
        Test: L'achat d'un document crée une transaction
        
        Exigence: 4.1
        """
        url = reverse('document-purchase', kwargs={'pk': self.document.id})
        
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('transaction_id', response.data)
        self.assertIn('payment_url', response.data)
        
        # Vérifier que la transaction a été créée
        transaction_id = response.data['transaction_id']
        transaction = Transaction.objects.get(id=transaction_id)
        
        self.assertEqual(transaction.utilisateur, self.user)
        self.assertEqual(transaction.type_transaction, 'ACHAT_DOCUMENT')
        self.assertEqual(transaction.montant, self.document.prix)
        self.assertEqual(transaction.statut, 'PENDING')
        self.assertEqual(transaction.reference_externe, str(self.document.id))
    
    def test_already_purchased_document_returns_download_link(self):
        """
        Test: Si l'utilisateur a déjà acheté le document, retourner le lien de téléchargement
        
        Exigence: 5.1
        """
        # Créer une transaction réussie
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=self.document.prix,
            statut='SUCCESS',
            reference_externe=str(self.document.id)
        )
        
        # Créer l'achat
        achat = AchatDocument.objects.create(
            acheteur=self.user,
            document=self.document,
            transaction=transaction,
            lien_telechargement='test_token',
            expiration_lien=timezone.now() + timedelta(hours=48)
        )
        
        url = reverse('document-purchase', kwargs={'pk': self.document.id})
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['already_purchased'])
        self.assertIn('download_url', response.data)
        self.assertIn('expiration', response.data)
    
    def test_secure_download_token_generation(self):
        """
        Test: Génération d'un token de téléchargement sécurisé
        
        Exigence: 5.1
        """
        token = SecureDownloadService.generate_download_token()
        
        self.assertIsNotNone(token)
        self.assertGreater(len(token), 20)  # Token doit être suffisamment long
    
    def test_download_link_expiration_48_hours(self):
        """
        Test: Les liens de téléchargement expirent après 48 heures
        
        Exigence: 5.1
        """
        # Créer une transaction et un achat
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=self.document.prix,
            statut='SUCCESS',
            reference_externe=str(self.document.id)
        )
        
        achat = AchatDocument.objects.create(
            acheteur=self.user,
            document=self.document,
            transaction=transaction,
            lien_telechargement='test_token',
            expiration_lien=timezone.now() - timedelta(hours=1)  # Expiré
        )
        
        # Vérifier que le lien est expiré
        is_expired = SecureDownloadService.is_link_expired(achat)
        self.assertTrue(is_expired)
        
        # Vérifier qu'un lien non expiré n'est pas marqué comme expiré
        achat.expiration_lien = timezone.now() + timedelta(hours=24)
        achat.save()
        
        is_expired = SecureDownloadService.is_link_expired(achat)
        self.assertFalse(is_expired)
    
    def test_regenerate_expired_link(self):
        """
        Test: Régénération d'un lien expiré
        
        Exigence: 5.4
        """
        # Créer une transaction et un achat avec lien expiré
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=self.document.prix,
            statut='SUCCESS',
            reference_externe=str(self.document.id)
        )
        
        achat = AchatDocument.objects.create(
            acheteur=self.user,
            document=self.document,
            transaction=transaction,
            lien_telechargement='old_token',
            expiration_lien=timezone.now() - timedelta(hours=1)
        )
        
        old_token = achat.lien_telechargement
        
        # Régénérer le lien
        new_link_info = SecureDownloadService.regenerate_link(achat)
        
        # Vérifier que le token a changé
        achat.refresh_from_db()
        self.assertNotEqual(achat.lien_telechargement, old_token)
        self.assertEqual(achat.lien_telechargement, new_link_info['token'])
        
        # Vérifier que la nouvelle expiration est dans 48h
        time_diff = achat.expiration_lien - timezone.now()
        self.assertGreater(time_diff.total_seconds(), 47 * 3600)  # Au moins 47h
        self.assertLess(time_diff.total_seconds(), 49 * 3600)  # Au plus 49h
    
    def test_purchase_history_endpoint(self):
        """
        Test: Endpoint de l'historique des achats
        
        Exigence: 5.3
        """
        # Créer plusieurs achats
        for i in range(3):
            transaction = Transaction.objects.create(
                utilisateur=self.user,
                type_transaction='ACHAT_DOCUMENT',
                montant=Decimal('5000.00'),
                statut='SUCCESS'
            )
            
            AchatDocument.objects.create(
                acheteur=self.user,
                document=self.document,
                transaction=transaction,
                lien_telechargement=f'token_{i}',
                expiration_lien=timezone.now() + timedelta(hours=48)
            )
        
        url = reverse('purchase-history-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
        # Vérifier les champs retournés
        achat_data = response.data['results'][0]
        self.assertIn('document_titre', achat_data)
        self.assertIn('document_culture', achat_data)
        self.assertIn('document_prix', achat_data)
        self.assertIn('lien_expire', achat_data)
        self.assertIn('peut_regenerer', achat_data)
        self.assertIn('nombre_telechargements', achat_data)
    
    def test_download_tracking(self):
        """
        Test: Enregistrement des téléchargements avec IP et timestamp
        
        Exigence: 5.5
        """
        # Créer une transaction et un achat
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=self.document.prix,
            statut='SUCCESS',
            reference_externe=str(self.document.id)
        )
        
        achat = AchatDocument.objects.create(
            acheteur=self.user,
            document=self.document,
            transaction=transaction,
            lien_telechargement='test_token',
            expiration_lien=timezone.now() + timedelta(hours=48)
        )
        
        initial_count = achat.nombre_telechargements
        
        # Enregistrer un téléchargement
        ip_address = '192.168.1.1'
        SecureDownloadService.track_download(achat, ip_address)
        
        # Vérifier que le compteur a été incrémenté
        achat.refresh_from_db()
        self.assertEqual(achat.nombre_telechargements, initial_count + 1)
        
        # Vérifier qu'un log a été créé
        log = DownloadLog.objects.filter(achat=achat).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.ip_address, ip_address)
        self.assertIsNotNone(log.timestamp)
    
    def test_inactive_document_cannot_be_purchased(self):
        """
        Test: Un document inactif ne peut pas être acheté
        """
        # Désactiver le document
        self.document.actif = False
        self.document.save()
        
        url = reverse('document-purchase', kwargs={'pk': self.document.id})
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('plus disponible', response.data['error'])
    
    def test_unauthenticated_user_cannot_purchase(self):
        """
        Test: Un utilisateur non authentifié ne peut pas acheter
        """
        # Déconnecter l'utilisateur
        self.client.force_authenticate(user=None)
        
        url = reverse('document-purchase', kwargs={'pk': self.document.id})
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_purchase_history_filtering_by_date(self):
        """
        Test: Filtrage de l'historique par plage de dates
        
        Exigence: 5.3
        """
        # Créer des achats à différentes dates
        base_date = timezone.now()
        
        for i in range(3):
            transaction = Transaction.objects.create(
                utilisateur=self.user,
                type_transaction='ACHAT_DOCUMENT',
                montant=Decimal('5000.00'),
                statut='SUCCESS'
            )
            
            achat = AchatDocument.objects.create(
                acheteur=self.user,
                document=self.document,
                transaction=transaction,
                lien_telechargement=f'token_{i}',
                expiration_lien=base_date + timedelta(hours=48)
            )
            
            # Modifier la date de création
            achat.created_at = base_date - timedelta(days=i)
            achat.save()
        
        # Filtrer par date
        date_debut = (base_date - timedelta(days=1)).isoformat()
        url = reverse('purchase-history-list')
        response = self.client.get(url, {'date_debut': date_debut})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Devrait retourner 2 achats (aujourd'hui et hier)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_purchase_history_filtering_by_culture(self):
        """
        Test: Filtrage de l'historique par culture
        
        Exigence: 5.3
        """
        # Créer un autre document avec une culture différente
        document_riz = DocumentTechnique.objects.create(
            template=self.template,
            titre='Document Test Riz',
            description='Document de test',
            prix=Decimal('6000.00'),
            region=self.region,
            prefecture=self.prefecture,
            canton=self.canton,
            culture='Riz',
            actif=True
        )
        
        # Créer des achats pour les deux cultures
        for doc in [self.document, document_riz]:
            transaction = Transaction.objects.create(
                utilisateur=self.user,
                type_transaction='ACHAT_DOCUMENT',
                montant=doc.prix,
                statut='SUCCESS'
            )
            
            AchatDocument.objects.create(
                acheteur=self.user,
                document=doc,
                transaction=transaction,
                lien_telechargement=f'token_{doc.id}',
                expiration_lien=timezone.now() + timedelta(hours=48)
            )
        
        # Filtrer par culture "Maïs"
        url = reverse('purchase-history-list')
        response = self.client.get(url, {'culture': 'Maïs'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['document_culture'], 'Maïs')
    
    def test_purchase_history_filtering_by_type(self):
        """
        Test: Filtrage de l'historique par type de document
        
        Exigence: 5.3
        """
        # Créer un template de type différent
        template_compte = DocumentTemplate.objects.create(
            titre='Template Compte',
            description='Template de test',
            type_document='COMPTE_EXPLOITATION',
            format_fichier='EXCEL',
            variables_requises=['canton', 'culture']
        )
        
        # Créer un document avec le nouveau template
        document_compte = DocumentTechnique.objects.create(
            template=template_compte,
            titre='Compte Exploitation Maïs',
            description='Document de test',
            prix=Decimal('7000.00'),
            region=self.region,
            prefecture=self.prefecture,
            canton=self.canton,
            culture='Maïs',
            actif=True
        )
        
        # Créer des achats pour les deux types
        # Achat 1: ITINERAIRE_TECHNIQUE (template par défaut)
        transaction1 = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=self.document.prix,
            statut='SUCCESS'
        )
        
        AchatDocument.objects.create(
            acheteur=self.user,
            document=self.document,
            transaction=transaction1,
            lien_telechargement=f'token_{self.document.id}',
            expiration_lien=timezone.now() + timedelta(hours=48)
        )
        
        # Achat 2: COMPTE_EXPLOITATION
        transaction2 = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=document_compte.prix,
            statut='SUCCESS'
        )
        
        AchatDocument.objects.create(
            acheteur=self.user,
            document=document_compte,
            transaction=transaction2,
            lien_telechargement=f'token_{document_compte.id}',
            expiration_lien=timezone.now() + timedelta(hours=48)
        )
        
        # Filtrer par type COMPTE_EXPLOITATION
        url = reverse('purchase-history-list')
        response = self.client.get(url, {'type_document': 'COMPTE_EXPLOITATION'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Vérifier que c'est bien le bon document
        achat_id = response.data['results'][0]['id']
        achat = AchatDocument.objects.get(id=achat_id)
        self.assertEqual(achat.document.template.type_document, 'COMPTE_EXPLOITATION')
    
    def test_purchase_history_filtering_by_expired_links(self):
        """
        Test: Filtrage de l'historique par liens expirés
        
        Exigence: 5.3, 5.4
        """
        # Créer des achats avec liens expirés et non expirés
        for i, expired in enumerate([True, False, True]):
            transaction = Transaction.objects.create(
                utilisateur=self.user,
                type_transaction='ACHAT_DOCUMENT',
                montant=Decimal('5000.00'),
                statut='SUCCESS'
            )
            
            expiration = timezone.now() - timedelta(hours=1) if expired else timezone.now() + timedelta(hours=48)
            
            AchatDocument.objects.create(
                acheteur=self.user,
                document=self.document,
                transaction=transaction,
                lien_telechargement=f'token_{i}',
                expiration_lien=expiration
            )
        
        # Filtrer par liens expirés
        url = reverse('purchase-history-list')
        response = self.client.get(url, {'lien_expire': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # Filtrer par liens non expirés
        response = self.client.get(url, {'lien_expire': 'false'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_purchase_history_pagination(self):
        """
        Test: Pagination de l'historique des achats
        
        Exigence: 5.3
        """
        # Créer 55 achats (plus que la limite de pagination de 50)
        for i in range(55):
            transaction = Transaction.objects.create(
                utilisateur=self.user,
                type_transaction='ACHAT_DOCUMENT',
                montant=Decimal('5000.00'),
                statut='SUCCESS'
            )
            
            AchatDocument.objects.create(
                acheteur=self.user,
                document=self.document,
                transaction=transaction,
                lien_telechargement=f'token_{i}',
                expiration_lien=timezone.now() + timedelta(hours=48)
            )
        
        # Première page
        url = reverse('purchase-history-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 55)
        self.assertEqual(len(response.data['results']), 50)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        
        # Deuxième page
        response = self.client.get(url, {'page': 2})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])
    
    def test_regenerate_link_endpoint(self):
        """
        Test: Endpoint de régénération de lien
        
        Exigence: 5.4
        """
        # Créer un achat avec lien expiré
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=self.document.prix,
            statut='SUCCESS',
            reference_externe=str(self.document.id)
        )
        
        achat = AchatDocument.objects.create(
            acheteur=self.user,
            document=self.document,
            transaction=transaction,
            lien_telechargement='old_token',
            expiration_lien=timezone.now() - timedelta(hours=1)
        )
        
        # Régénérer le lien via l'API
        url = reverse('purchase-history-regenerate-link', kwargs={'pk': achat.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('download_url', response.data)
        self.assertIn('expiration', response.data)
        
        # Vérifier que le token a changé
        achat.refresh_from_db()
        self.assertNotEqual(achat.lien_telechargement, 'old_token')
    
    def test_user_can_only_see_own_purchases(self):
        """
        Test: Un utilisateur ne peut voir que ses propres achats
        
        Exigence: 5.3
        """
        # Créer un autre utilisateur
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            phone_number='+22890123457',
            password='testpass123',
            user_type='ACHETEUR'
        )
        
        # Créer des achats pour les deux utilisateurs
        for user in [self.user, other_user]:
            transaction = Transaction.objects.create(
                utilisateur=user,
                type_transaction='ACHAT_DOCUMENT',
                montant=Decimal('5000.00'),
                statut='SUCCESS'
            )
            
            AchatDocument.objects.create(
                acheteur=user,
                document=self.document,
                transaction=transaction,
                lien_telechargement=f'token_{user.id}',
                expiration_lien=timezone.now() + timedelta(hours=48)
            )
        
        # Vérifier que l'utilisateur ne voit que ses achats
        url = reverse('purchase-history-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        # Vérifier que l'achat appartient bien à l'utilisateur connecté
        achat_id = response.data['results'][0]['id']
        achat = AchatDocument.objects.get(id=achat_id)
        self.assertEqual(achat.acheteur, self.user)
    
    def test_download_log_records_multiple_downloads(self):
        """
        Test: Enregistrement de plusieurs téléchargements
        
        Exigence: 5.5
        """
        # Créer un achat
        transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=self.document.prix,
            statut='SUCCESS',
            reference_externe=str(self.document.id)
        )
        
        achat = AchatDocument.objects.create(
            acheteur=self.user,
            document=self.document,
            transaction=transaction,
            lien_telechargement='test_token',
            expiration_lien=timezone.now() + timedelta(hours=48)
        )
        
        # Enregistrer plusieurs téléchargements
        ip_addresses = ['192.168.1.1', '192.168.1.2', '192.168.1.1']
        
        for ip in ip_addresses:
            SecureDownloadService.track_download(achat, ip)
        
        # Vérifier le compteur
        achat.refresh_from_db()
        self.assertEqual(achat.nombre_telechargements, 3)
        
        # Vérifier les logs
        logs = DownloadLog.objects.filter(achat=achat).order_by('timestamp')
        self.assertEqual(logs.count(), 3)
        
        # Vérifier les adresses IP
        log_ips = [log.ip_address for log in logs]
        self.assertEqual(log_ips, ip_addresses)
