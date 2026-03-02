"""
Tests pour le service de chiffrement AES-256-GCM
Valide les exigences 33.2 et 33.3
"""

import pytest
from django.test import TestCase, override_settings
from django.conf import settings
from apps.core.encryption import EncryptionService, get_encryption_service


class EncryptionServiceTest(TestCase):
    """Tests du service de chiffrement"""
    
    def setUp(self):
        """Initialise le service de chiffrement pour les tests"""
        self.service = get_encryption_service()
    
    def test_encrypt_decrypt_basic(self):
        """Test: Chiffrement et déchiffrement basique"""
        plaintext = "Données sensibles"
        
        # Chiffrer
        encrypted = self.service.encrypt(plaintext)
        
        # Vérifier que le texte est chiffré
        self.assertNotEqual(encrypted, plaintext)
        self.assertIsInstance(encrypted, str)
        
        # Déchiffrer
        decrypted = self.service.decrypt(encrypted)
        
        # Vérifier que le déchiffrement fonctionne
        self.assertEqual(decrypted, plaintext)
    
    def test_encrypt_empty_string_raises_error(self):
        """Test: Chiffrer une chaîne vide lève une erreur"""
        with self.assertRaises(ValueError):
            self.service.encrypt("")
    
    def test_decrypt_empty_string_raises_error(self):
        """Test: Déchiffrer une chaîne vide lève une erreur"""
        with self.assertRaises(ValueError):
            self.service.decrypt("")
    
    def test_encrypt_unicode_characters(self):
        """Test: Chiffrement de caractères Unicode"""
        plaintext = "Données avec accents: éàèùç, émojis: 🔒🔐, chinois: 中文"
        
        encrypted = self.service.encrypt(plaintext)
        decrypted = self.service.decrypt(encrypted)
        
        self.assertEqual(decrypted, plaintext)
    
    def test_encrypt_long_text(self):
        """Test: Chiffrement de texte long"""
        plaintext = "A" * 10000  # 10KB de texte
        
        encrypted = self.service.encrypt(plaintext)
        decrypted = self.service.decrypt(encrypted)
        
        self.assertEqual(decrypted, plaintext)
    
    def test_encrypt_produces_different_ciphertext(self):
        """Test: Chiffrer le même texte produit des ciphertexts différents (nonce unique)"""
        plaintext = "Données sensibles"
        
        encrypted1 = self.service.encrypt(plaintext)
        encrypted2 = self.service.encrypt(plaintext)
        
        # Les ciphertexts doivent être différents (nonce unique)
        self.assertNotEqual(encrypted1, encrypted2)
        
        # Mais les deux doivent déchiffrer au même plaintext
        self.assertEqual(self.service.decrypt(encrypted1), plaintext)
        self.assertEqual(self.service.decrypt(encrypted2), plaintext)
    
    def test_decrypt_invalid_data_raises_error(self):
        """Test: Déchiffrer des données invalides lève une erreur"""
        invalid_data = "invalid-base64-data"
        
        with self.assertRaises(ValueError):
            self.service.decrypt(invalid_data)
    
    def test_decrypt_tampered_data_raises_error(self):
        """Test: Déchiffrer des données modifiées lève une erreur (authentification)"""
        plaintext = "Données sensibles"
        encrypted = self.service.encrypt(plaintext)
        
        # Modifier le ciphertext
        import base64
        encrypted_bytes = base64.b64decode(encrypted.encode('utf-8'))
        tampered_bytes = encrypted_bytes[:-1] + b'X'  # Modifier le dernier byte
        tampered_encrypted = base64.b64encode(tampered_bytes).decode('utf-8')
        
        # Le déchiffrement doit échouer (authentification GCM)
        with self.assertRaises(ValueError):
            self.service.decrypt(tampered_encrypted)
    
    def test_encrypt_special_characters(self):
        """Test: Chiffrement de caractères spéciaux"""
        plaintext = "!@#$%^&*()_+-=[]{}|;':\",./<>?\n\t\r"
        
        encrypted = self.service.encrypt(plaintext)
        decrypted = self.service.decrypt(encrypted)
        
        self.assertEqual(decrypted, plaintext)
    
    def test_encrypt_numbers(self):
        """Test: Chiffrement de nombres (convertis en string)"""
        plaintext = "1234567890"
        
        encrypted = self.service.encrypt(plaintext)
        decrypted = self.service.decrypt(encrypted)
        
        self.assertEqual(decrypted, plaintext)
    
    def test_singleton_service(self):
        """Test: get_encryption_service retourne toujours la même instance"""
        service1 = get_encryption_service()
        service2 = get_encryption_service()
        
        self.assertIs(service1, service2)
    
    @override_settings(ENCRYPTION_KEY='')
    def test_missing_encryption_key_raises_error(self):
        """Test: Absence de clé de chiffrement lève une erreur"""
        # Réinitialiser le singleton
        import apps.core.encryption
        apps.core.encryption._encryption_service = None
        
        with self.assertRaises(ValueError) as context:
            get_encryption_service()
        
        self.assertIn("ENCRYPTION_KEY", str(context.exception))
    
    def test_encrypted_data_is_base64(self):
        """Test: Les données chiffrées sont en base64 valide"""
        plaintext = "Données sensibles"
        encrypted = self.service.encrypt(plaintext)
        
        # Vérifier que c'est du base64 valide
        import base64
        try:
            decoded = base64.b64decode(encrypted.encode('utf-8'))
            self.assertIsInstance(decoded, bytes)
            self.assertGreater(len(decoded), 12)  # Au moins nonce (12 bytes) + données
        except Exception as e:
            self.fail(f"Les données chiffrées ne sont pas en base64 valide: {e}")
    
    def test_encrypt_multiline_text(self):
        """Test: Chiffrement de texte multiligne"""
        plaintext = """Ligne 1
Ligne 2
Ligne 3
Avec des espaces    et des tabulations\t"""
        
        encrypted = self.service.encrypt(plaintext)
        decrypted = self.service.decrypt(encrypted)
        
        self.assertEqual(decrypted, plaintext)


class EncryptionPerformanceTest(TestCase):
    """Tests de performance du chiffrement"""
    
    def setUp(self):
        self.service = get_encryption_service()
    
    def test_encrypt_performance(self):
        """Test: Performance du chiffrement (doit être rapide)"""
        import time
        
        plaintext = "Données sensibles" * 100  # ~1.7KB
        
        start = time.time()
        for _ in range(100):
            self.service.encrypt(plaintext)
        duration = time.time() - start
        
        # 100 chiffrements doivent prendre moins de 1 seconde
        self.assertLess(duration, 1.0, 
                       f"Chiffrement trop lent: {duration:.3f}s pour 100 opérations")
    
    def test_decrypt_performance(self):
        """Test: Performance du déchiffrement (doit être rapide)"""
        import time
        
        plaintext = "Données sensibles" * 100
        encrypted = self.service.encrypt(plaintext)
        
        start = time.time()
        for _ in range(100):
            self.service.decrypt(encrypted)
        duration = time.time() - start
        
        # 100 déchiffrements doivent prendre moins de 1 seconde
        self.assertLess(duration, 1.0,
                       f"Déchiffrement trop lent: {duration:.3f}s pour 100 opérations")


class EncryptionSecurityTest(TestCase):
    """Tests de sécurité du chiffrement"""
    
    def setUp(self):
        self.service = get_encryption_service()
    
    def test_nonce_uniqueness(self):
        """Test: Les nonces sont uniques pour chaque chiffrement"""
        plaintext = "Données sensibles"
        
        # Générer 100 chiffrements
        encrypted_list = [self.service.encrypt(plaintext) for _ in range(100)]
        
        # Extraire les nonces
        import base64
        nonces = []
        for encrypted in encrypted_list:
            encrypted_bytes = base64.b64decode(encrypted.encode('utf-8'))
            nonce = encrypted_bytes[:12]
            nonces.append(nonce)
        
        # Vérifier que tous les nonces sont uniques
        unique_nonces = set(nonces)
        self.assertEqual(len(unique_nonces), 100,
                        "Les nonces ne sont pas uniques!")
    
    def test_ciphertext_length(self):
        """Test: La longueur du ciphertext est appropriée"""
        plaintext = "Test"
        encrypted = self.service.encrypt(plaintext)
        
        import base64
        encrypted_bytes = base64.b64decode(encrypted.encode('utf-8'))
        
        # Longueur = nonce (12) + plaintext + tag (16)
        expected_min_length = 12 + len(plaintext.encode('utf-8')) + 16
        self.assertGreaterEqual(len(encrypted_bytes), expected_min_length)
    
    def test_no_plaintext_leakage(self):
        """Test: Le ciphertext ne contient pas le plaintext en clair"""
        plaintext = "MotDePasseSecret123"
        encrypted = self.service.encrypt(plaintext)
        
        # Vérifier que le plaintext n'apparaît pas dans le ciphertext
        self.assertNotIn(plaintext, encrypted)
        self.assertNotIn(plaintext.lower(), encrypted.lower())
        
        # Vérifier en base64 décodé aussi
        import base64
        encrypted_bytes = base64.b64decode(encrypted.encode('utf-8'))
        self.assertNotIn(plaintext.encode('utf-8'), encrypted_bytes)


# Tests d'intégration avec pytest pour property-based testing
@pytest.mark.django_db
class TestEncryptionProperties:
    """Tests basés sur les propriétés du chiffrement"""
    
    def test_encryption_is_reversible(self):
        """Propriété: encrypt(decrypt(x)) == x pour tout x"""
        service = get_encryption_service()
        
        test_cases = [
            "Simple text",
            "Texte avec accents: éàèùç",
            "Numbers: 1234567890",
            "Special: !@#$%^&*()",
            "Long: " + "A" * 1000,
            "Unicode: 🔒🔐 中文",
        ]
        
        for plaintext in test_cases:
            encrypted = service.encrypt(plaintext)
            decrypted = service.decrypt(encrypted)
            assert decrypted == plaintext, f"Failed for: {plaintext[:50]}"
    
    def test_encryption_is_deterministic_in_decryption(self):
        """Propriété: decrypt(x) produit toujours le même résultat"""
        service = get_encryption_service()
        
        plaintext = "Test data"
        encrypted = service.encrypt(plaintext)
        
        # Déchiffrer plusieurs fois
        results = [service.decrypt(encrypted) for _ in range(10)]
        
        # Tous les résultats doivent être identiques
        assert all(r == plaintext for r in results)
    
    def test_encryption_is_non_deterministic(self):
        """Propriété: encrypt(x) produit des résultats différents à chaque fois"""
        service = get_encryption_service()
        
        plaintext = "Test data"
        
        # Chiffrer plusieurs fois
        encrypted_list = [service.encrypt(plaintext) for _ in range(10)]
        
        # Tous les ciphertexts doivent être différents
        assert len(set(encrypted_list)) == 10
