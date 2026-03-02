"""
Service de chiffrement pour les données sensibles
Implémente le chiffrement AES-256-GCM pour les documents d'identité et autres données sensibles
"""

import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from typing import Optional


class EncryptionService:
    """
    Service de chiffrement/déchiffrement AES-256-GCM
    
    Utilise AES-256 en mode GCM (Galois/Counter Mode) qui fournit:
    - Chiffrement authentifié (AEAD - Authenticated Encryption with Associated Data)
    - Protection contre les modifications
    - Nonce unique pour chaque opération
    """
    
    def __init__(self):
        """Initialise le service avec la clé de chiffrement depuis les variables d'environnement"""
        encryption_key = getattr(settings, 'ENCRYPTION_KEY', None)
        
        if not encryption_key:
            raise ValueError(
                "ENCRYPTION_KEY n'est pas définie dans les variables d'environnement. "
                "Générez une clé avec: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        
        # Dériver une clé de 32 bytes (256 bits) depuis la clé fournie
        self.key = self._derive_key(encryption_key)
        self.aesgcm = AESGCM(self.key)
    
    def _derive_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Dérive une clé de 32 bytes depuis un mot de passe en utilisant PBKDF2
        
        Args:
            password: Le mot de passe/clé source
            salt: Salt optionnel (utilise un salt fixe si non fourni pour la cohérence)
        
        Returns:
            Clé de 32 bytes
        """
        if salt is None:
            # Utiliser un salt fixe dérivé du SECRET_KEY pour la cohérence
            # En production, on pourrait stocker le salt séparément
            salt = settings.SECRET_KEY[:16].encode('utf-8')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,  # Recommandation NIST
        )
        return kdf.derive(password.encode('utf-8'))
    
    def encrypt(self, plaintext: str) -> str:
        """
        Chiffre une chaîne de caractères avec AES-256-GCM
        
        Args:
            plaintext: Texte en clair à chiffrer
        
        Returns:
            Texte chiffré encodé en base64 (format: nonce + ciphertext)
        
        Raises:
            ValueError: Si le plaintext est vide
        """
        if not plaintext:
            raise ValueError("Le texte à chiffrer ne peut pas être vide")
        
        # Générer un nonce aléatoire de 12 bytes (recommandé pour GCM)
        nonce = os.urandom(12)
        
        # Chiffrer les données
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = self.aesgcm.encrypt(nonce, plaintext_bytes, None)
        
        # Combiner nonce + ciphertext et encoder en base64
        encrypted_data = nonce + ciphertext
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Déchiffre une chaîne de caractères chiffrée avec AES-256-GCM
        
        Args:
            encrypted_text: Texte chiffré encodé en base64
        
        Returns:
            Texte en clair déchiffré
        
        Raises:
            ValueError: Si le texte chiffré est invalide
            cryptography.exceptions.InvalidTag: Si l'authentification échoue
        """
        if not encrypted_text:
            raise ValueError("Le texte chiffré ne peut pas être vide")
        
        try:
            # Décoder depuis base64
            encrypted_data = base64.b64decode(encrypted_text.encode('utf-8'))
            
            # Extraire le nonce (12 premiers bytes) et le ciphertext
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            
            # Déchiffrer
            plaintext_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext_bytes.decode('utf-8')
        
        except Exception as e:
            raise ValueError(f"Échec du déchiffrement: {str(e)}")


# Instance singleton du service de chiffrement
_encryption_service = None


def get_encryption_service() -> EncryptionService:
    """
    Retourne l'instance singleton du service de chiffrement
    
    Returns:
        Instance de EncryptionService
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
