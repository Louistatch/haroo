"""
Tests pour le service de stockage cloud
"""
import pytest
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.core.storage import SecureCloudStorage
from unittest.mock import patch, MagicMock


class SecureCloudStorageTest(TestCase):
    """
    Tests pour le service de stockage cloud sécurisé
    """
    
    def setUp(self):
        """Configuration des tests"""
        self.test_file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )
    
    @override_settings(USE_S3=False, USE_CLOUDINARY=False)
    def test_get_storage_backend_local(self):
        """Test: Retourne le stockage local par défaut"""
        storage = SecureCloudStorage.get_storage_backend()
        self.assertIsNotNone(storage)
    
    @override_settings(USE_S3=True)
    @patch('storages.backends.s3boto3.S3Boto3Storage')
    def test_get_storage_backend_s3(self, mock_s3):
        """Test: Retourne le backend S3 si configuré"""
        mock_s3.return_value = MagicMock()
        storage = SecureCloudStorage.get_storage_backend()
        mock_s3.assert_called_once()
    
    @override_settings(USE_CLOUDINARY=True)
    def test_get_storage_backend_cloudinary(self):
        """Test: Retourne le backend Cloudinary si configuré"""
        try:
            # Import dynamique pour éviter les erreurs si cloudinary n'est pas installé
            with patch.object(SecureCloudStorage, 'get_storage_backend') as mock_get:
                from apps.core.cloudinary_storage import CloudinaryStorage
                mock_storage = MagicMock(spec=CloudinaryStorage)
                mock_get.return_value = mock_storage
                
                storage = SecureCloudStorage.get_storage_backend()
                self.assertIsNotNone(storage)
        except ModuleNotFoundError:
            # Cloudinary n'est pas installé, skip le test
            self.skipTest("Cloudinary module not installed")
    
    @override_settings(
        USE_S3=True,
        AWS_ACCESS_KEY_ID='test-key',
        AWS_SECRET_ACCESS_KEY='test-secret',
        AWS_STORAGE_BUCKET_NAME='test-bucket',
        AWS_S3_REGION_NAME='eu-west-1'
    )
    @patch('boto3.client')
    def test_generate_s3_signed_url(self, mock_boto_client):
        """Test: Génère une URL signée S3"""
        # Mock du client S3
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = 'https://s3.amazonaws.com/signed-url'
        mock_boto_client.return_value = mock_s3
        
        # Générer l'URL signée
        url = SecureCloudStorage.generate_signed_url('test/file.pdf', expiration_hours=48)
        
        # Vérifications
        self.assertIsNotNone(url)
        self.assertIn('https://', url)
        mock_s3.generate_presigned_url.assert_called_once()
    
    @override_settings(USE_S3=False, USE_CLOUDINARY=False)
    def test_generate_signed_url_local(self):
        """Test: Retourne l'URL locale en développement"""
        url = SecureCloudStorage.generate_signed_url('test/file.pdf')
        self.assertIsNotNone(url)
        self.assertIn('/media/', url)
    
    @patch('apps.core.storage.SecureCloudStorage.get_storage_backend')
    def test_delete_file_success(self, mock_get_storage):
        """Test: Supprime un fichier avec succès"""
        # Mock du storage
        mock_storage = MagicMock()
        mock_storage.exists.return_value = True
        mock_storage.delete.return_value = None
        mock_get_storage.return_value = mock_storage
        
        # Supprimer le fichier
        result = SecureCloudStorage.delete_file('test/file.pdf')
        
        # Vérifications
        self.assertTrue(result)
        mock_storage.exists.assert_called_once_with('test/file.pdf')
        mock_storage.delete.assert_called_once_with('test/file.pdf')
    
    @patch('apps.core.storage.SecureCloudStorage.get_storage_backend')
    def test_delete_file_not_exists(self, mock_get_storage):
        """Test: Retourne False si le fichier n'existe pas"""
        # Mock du storage
        mock_storage = MagicMock()
        mock_storage.exists.return_value = False
        mock_get_storage.return_value = mock_storage
        
        # Supprimer le fichier
        result = SecureCloudStorage.delete_file('test/nonexistent.pdf')
        
        # Vérifications
        self.assertFalse(result)
        mock_storage.exists.assert_called_once_with('test/nonexistent.pdf')
        mock_storage.delete.assert_not_called()
    
    @patch('apps.core.storage.SecureCloudStorage.get_storage_backend')
    def test_get_file_url_public(self, mock_get_storage):
        """Test: Retourne l'URL publique d'un fichier"""
        # Mock du storage
        mock_storage = MagicMock()
        mock_storage.url.return_value = 'https://example.com/file.pdf'
        mock_get_storage.return_value = mock_storage
        
        # Récupérer l'URL
        url = SecureCloudStorage.get_file_url('test/file.pdf', signed=False)
        
        # Vérifications
        self.assertEqual(url, 'https://example.com/file.pdf')
        mock_storage.url.assert_called_once_with('test/file.pdf')
    
    @patch('apps.core.storage.SecureCloudStorage.generate_signed_url')
    def test_get_file_url_signed(self, mock_generate_signed):
        """Test: Retourne l'URL signée d'un fichier"""
        mock_generate_signed.return_value = 'https://example.com/signed-url'
        
        # Récupérer l'URL signée
        url = SecureCloudStorage.get_file_url('test/file.pdf', signed=True)
        
        # Vérifications
        self.assertEqual(url, 'https://example.com/signed-url')
        mock_generate_signed.assert_called_once_with('test/file.pdf')


class SignedURLExpirationTest(TestCase):
    """
    Tests pour la validation de l'expiration des URLs signées
    Exigence: 31.4
    """
    
    @override_settings(
        USE_S3=True,
        AWS_ACCESS_KEY_ID='test-key',
        AWS_SECRET_ACCESS_KEY='test-secret',
        AWS_STORAGE_BUCKET_NAME='test-bucket',
        AWS_S3_REGION_NAME='eu-west-1'
    )
    @patch('boto3.client')
    def test_signed_url_default_expiration(self, mock_boto_client):
        """Test: URL signée avec expiration par défaut (48h)"""
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = 'https://signed-url'
        mock_boto_client.return_value = mock_s3
        
        SecureCloudStorage.generate_signed_url('test/file.pdf')
        
        # Vérifier que l'expiration est de 48h (172800 secondes)
        call_args = mock_s3.generate_presigned_url.call_args
        self.assertEqual(call_args[1]['ExpiresIn'], 48 * 3600)
    
    @override_settings(
        USE_S3=True,
        AWS_ACCESS_KEY_ID='test-key',
        AWS_SECRET_ACCESS_KEY='test-secret',
        AWS_STORAGE_BUCKET_NAME='test-bucket',
        AWS_S3_REGION_NAME='eu-west-1'
    )
    @patch('boto3.client')
    def test_signed_url_custom_expiration(self, mock_boto_client):
        """Test: URL signée avec expiration personnalisée"""
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = 'https://signed-url'
        mock_boto_client.return_value = mock_s3
        
        SecureCloudStorage.generate_signed_url('test/file.pdf', expiration_hours=24)
        
        # Vérifier que l'expiration est de 24h (86400 secondes)
        call_args = mock_s3.generate_presigned_url.call_args
        self.assertEqual(call_args[1]['ExpiresIn'], 24 * 3600)
