"""
Tests pour les modèles de documents
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.documents.models import DocumentTemplate, DocumentTechnique, AchatDocument
from apps.locations.models import Region, Prefecture, Canton
from apps.payments.models import Transaction
from decimal import Decimal

User = get_user_model()


class DocumentTemplateModelTest(TestCase):
    """Tests pour le modèle DocumentTemplate"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.template = DocumentTemplate.objects.create(
            titre="Compte d'Exploitation Maïs",
            description="Template pour compte d'exploitation du maïs",
            type_document='COMPTE_EXPLOITATION',
            format_fichier='EXCEL',
            fichier_template='templates/test.xlsx',
            variables_requises=['canton', 'culture', 'prix'],
            version=1
        )
    
    def test_template_creation(self):
        """Test de création d'un template"""
        self.assertEqual(self.template.titre, "Compte d'Exploitation Maïs")
        self.assertEqual(self.template.type_document, 'COMPTE_EXPLOITATION')
        self.assertEqual(self.template.format_fichier, 'EXCEL')
        self.assertEqual(len(self.template.variables_requises), 3)
        self.assertEqual(self.template.version, 1)
    
    def test_template_str(self):
        """Test de la représentation string du template"""
        expected = f"{self.template.titre} (v{self.template.version})"
        self.assertEqual(str(self.template), expected)


class DocumentTechniqueModelTest(TestCase):
    """Tests pour le modèle DocumentTechnique"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
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
        
        # Créer un template
        self.template = DocumentTemplate.objects.create(
            titre="Itinéraire Technique Maïs",
            description="Itinéraire technique pour la culture du maïs",
            type_document='ITINERAIRE_TECHNIQUE',
            format_fichier='WORD',
            fichier_template='templates/itineraire.docx',
            variables_requises=['canton', 'culture'],
            version=1
        )
        
        # Créer un document technique
        self.document = DocumentTechnique.objects.create(
            template=self.template,
            titre="Itinéraire Technique Maïs - Lomé 1er",
            description="Document personnalisé pour Lomé 1er",
            prix=Decimal('5000.00'),
            region=self.region,
            prefecture=self.prefecture,
            canton=self.canton,
            culture="Maïs",
            fichier_genere='documents/mais_lome1.docx',
            actif=True
        )
    
    def test_document_creation(self):
        """Test de création d'un document technique"""
        self.assertEqual(self.document.titre, "Itinéraire Technique Maïs - Lomé 1er")
        self.assertEqual(self.document.prix, Decimal('5000.00'))
        self.assertEqual(self.document.culture, "Maïs")
        self.assertTrue(self.document.actif)
    
    def test_document_relationships(self):
        """Test des relations du document"""
        self.assertEqual(self.document.template, self.template)
        self.assertEqual(self.document.region, self.region)
        self.assertEqual(self.document.prefecture, self.prefecture)
        self.assertEqual(self.document.canton, self.canton)
    
    def test_document_str(self):
        """Test de la représentation string du document"""
        self.assertEqual(str(self.document), self.document.titre)


class AchatDocumentModelTest(TestCase):
    """Tests pour le modèle AchatDocument"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            phone_number='+22890123456',
            user_type='ACHETEUR'
        )
        
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
        
        # Créer un template et un document
        self.template = DocumentTemplate.objects.create(
            titre="Test Template",
            description="Template de test",
            type_document='COMPTE_EXPLOITATION',
            format_fichier='EXCEL',
            fichier_template='templates/test.xlsx',
            variables_requises=['canton'],
            version=1
        )
        
        self.document = DocumentTechnique.objects.create(
            template=self.template,
            titre="Document Test",
            description="Document de test",
            prix=Decimal('3000.00'),
            canton=self.canton,
            culture="Riz",
            fichier_genere='documents/test.xlsx',
            actif=True
        )
        
        # Créer une transaction
        self.transaction = Transaction.objects.create(
            utilisateur=self.user,
            type_transaction='ACHAT_DOCUMENT',
            montant=Decimal('3000.00'),
            commission_plateforme=Decimal('0.00'),
            statut='SUCCESS'
        )
        
        # Créer un achat
        self.achat = AchatDocument.objects.create(
            acheteur=self.user,
            document=self.document,
            transaction=self.transaction,
            lien_telechargement='https://example.com/download/abc123',
            nombre_telechargements=0
        )
    
    def test_achat_creation(self):
        """Test de création d'un achat de document"""
        self.assertEqual(self.achat.acheteur, self.user)
        self.assertEqual(self.achat.document, self.document)
        self.assertEqual(self.achat.transaction, self.transaction)
        self.assertEqual(self.achat.nombre_telechargements, 0)
    
    def test_achat_relationships(self):
        """Test des relations de l'achat"""
        self.assertEqual(self.achat.acheteur.username, 'testuser')
        self.assertEqual(self.achat.document.titre, "Document Test")
        self.assertEqual(self.achat.transaction.statut, 'SUCCESS')
    
    def test_achat_str(self):
        """Test de la représentation string de l'achat"""
        expected = f"{self.user.get_full_name()} - {self.document.titre}"
        self.assertEqual(str(self.achat), expected)
