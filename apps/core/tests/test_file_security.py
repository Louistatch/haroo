"""
Tests pour les services de sécurité des fichiers
"""
import pytest
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.core.file_security import AntivirusService, MimeTypeValidator
from unittest.mock import patch, MagicMock
import subprocess


class AntivirusServiceTest(TestCase):
    """
    Tests pour le service de scan antivirus
    Exigences: 31.5, 31.6
    """
    
    def setUp(self):
        """Configuration des tests"""
        self.safe_file = SimpleUploadedFile(
            "safe.pdf",
            b"PDF content here",
            content_type="application/pdf"
        )
        
        # Fichier de test EICAR (standard pour tester les antivirus)
        self.eicar_file = SimpleUploadedFile(
            "eicar.txt",
            b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*',
            content_type="text/plain"
        )
    
    @patch('subprocess.run')
    def test_clamav_available(self, mock_run):
        """Test: Détecte si ClamAV est disponible"""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = AntivirusService._is_clamav_available()
        
        self.assertTrue(result)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_clamav_not_available(self, mock_run):
        """Test: Détecte si ClamAV n'est pas disponible"""
        mock_run.side_effect = FileNotFoundError()
        
        result = AntivirusService._is_clamav_available()
        
        self.assertFalse(result)
    
    @patch('apps.core.file_security.AntivirusService._is_clamav_available')
    @patch('apps.core.file_security.AntivirusService._scan_with_clamav')
    def test_scan_file_with_clamav(self, mock_scan_clamav, mock_is_available):
        """Test: Utilise ClamAV si disponible"""
        mock_is_available.return_value = True
        mock_scan_clamav.return_value = {
            'is_safe': True,
            'threat_found': False,
            'details': 'Aucune menace détectée',
            'scanner': 'ClamAV'
        }
        
        result = AntivirusService.scan_file(self.safe_file)
        
        self.assertTrue(result['is_safe'])
        self.assertFalse(result['threat_found'])
        mock_scan_clamav.assert_called_once()
    
    @patch('apps.core.file_security.AntivirusService._is_clamav_available')
    @patch('apps.core.file_security.AntivirusService._basic_scan')
    def test_scan_file_fallback_to_basic(self, mock_basic_scan, mock_is_available):
        """Test: Utilise le scan basique si ClamAV non disponible"""
        mock_is_available.return_value = False
        mock_basic_scan.return_value = {
            'is_safe': True,
            'threat_found': False,
            'details': 'Aucune menace détectée (scan basique)',
            'scanner': 'Basic'
        }
        
        result = AntivirusService.scan_file(self.safe_file)
        
        self.assertTrue(result['is_safe'])
        self.assertEqual(result['scanner'], 'Basic')
        mock_basic_scan.assert_called_once()
    
    def test_basic_scan_safe_file(self):
        """Test: Scan basique détecte un fichier sûr"""
        result = AntivirusService._basic_scan(self.safe_file)
        
        self.assertTrue(result['is_safe'])
        self.assertFalse(result['threat_found'])
        self.assertEqual(result['scanner'], 'Basic')
    
    def test_basic_scan_eicar_file(self):
        """Test: Scan basique détecte le fichier de test EICAR"""
        result = AntivirusService._basic_scan(self.eicar_file)
        
        self.assertFalse(result['is_safe'])
        self.assertTrue(result['threat_found'])
        self.assertIn('Signature malveillante', result['details'])
    
    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_clamav_scan_clean_file(self, mock_unlink, mock_tempfile, mock_run):
        """Test: ClamAV détecte un fichier propre"""
        # Mock du fichier temporaire
        mock_temp = MagicMock()
        mock_temp.name = 'test.pdf'
        mock_temp.__enter__ = MagicMock(return_value=mock_temp)
        mock_temp.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_temp
        
        # Mock de ClamAV retournant un fichier propre
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='OK'
        )
        
        result = AntivirusService._scan_with_clamav(self.safe_file)
        
        self.assertTrue(result['is_safe'])
        self.assertFalse(result['threat_found'])
    
    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_clamav_scan_infected_file(self, mock_unlink, mock_tempfile, mock_run):
        """Test: ClamAV détecte un fichier infecté"""
        # Mock du fichier temporaire
        mock_temp = MagicMock()
        mock_temp.name = 'test.pdf'
        mock_temp.__enter__ = MagicMock(return_value=mock_temp)
        mock_temp.__exit__ = MagicMock(return_value=False)
        mock_tempfile.return_value = mock_temp
        
        # Mock de ClamAV retournant un virus
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout='Eicar-Test-Signature FOUND'
        )
        
        result = AntivirusService._scan_with_clamav(self.eicar_file)
        
        self.assertFalse(result['is_safe'])
        self.assertTrue(result['threat_found'])
        self.assertIn('FOUND', result['details'])
    
    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    def test_clamav_scan_timeout(self, mock_tempfile, mock_run):
        """Test: Gère le timeout du scan ClamAV"""
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test.pdf'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Simuler un timeout
        mock_run.side_effect = subprocess.TimeoutExpired('clamscan', 30)
        
        result = AntivirusService._scan_with_clamav(self.safe_file)
        
        self.assertFalse(result['is_safe'])
        self.assertIn('Timeout', result['details'])


class MimeTypeValidatorTest(TestCase):
    """
    Tests pour le validateur de types MIME
    Exigences: 31.1, 31.5
    """
    
    def test_validate_image_mime_type_valid(self):
        """Test: Valide un type MIME image autorisé"""
        file = SimpleUploadedFile(
            "test.jpg",
            b"image content",
            content_type="image/jpeg"
        )
        
        result = MimeTypeValidator.validate_mime_type(file, category='image')
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_image_mime_type_invalid(self):
        """Test: Rejette un type MIME image non autorisé"""
        file = SimpleUploadedFile(
            "test.bmp",
            b"image content",
            content_type="image/bmp"
        )
        
        result = MimeTypeValidator.validate_mime_type(file, category='image')
        
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)
        self.assertIn('non autorisé', result['errors'][0])
    
    def test_validate_document_mime_type_pdf(self):
        """Test: Valide un PDF"""
        file = SimpleUploadedFile(
            "test.pdf",
            b"PDF content",
            content_type="application/pdf"
        )
        
        result = MimeTypeValidator.validate_mime_type(file, category='document')
        
        self.assertTrue(result['is_valid'])
    
    def test_validate_document_mime_type_excel(self):
        """Test: Valide un fichier Excel"""
        file = SimpleUploadedFile(
            "test.xlsx",
            b"Excel content",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        result = MimeTypeValidator.validate_mime_type(file, category='document')
        
        self.assertTrue(result['is_valid'])
    
    def test_validate_document_mime_type_word(self):
        """Test: Valide un fichier Word"""
        file = SimpleUploadedFile(
            "test.docx",
            b"Word content",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        result = MimeTypeValidator.validate_mime_type(file, category='document')
        
        self.assertTrue(result['is_valid'])
    
    def test_validate_mime_type_no_content_type(self):
        """Test: Rejette un fichier sans type MIME"""
        file = SimpleUploadedFile("test.pdf", b"content")
        delattr(file, 'content_type')
        
        result = MimeTypeValidator.validate_mime_type(file, category='document')
        
        self.assertFalse(result['is_valid'])
        self.assertIn('Type MIME non fourni', result['errors'][0])
    
    def test_validate_mime_type_executable(self):
        """Test: Rejette un fichier exécutable"""
        file = SimpleUploadedFile(
            "malware.exe",
            b"executable content",
            content_type="application/x-msdownload"
        )
        
        result = MimeTypeValidator.validate_mime_type(file, category='document')
        
        self.assertFalse(result['is_valid'])
