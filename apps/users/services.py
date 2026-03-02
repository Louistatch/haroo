"""
Services pour la gestion de l'authentification et des utilisateurs
"""
import random
import string
import hashlib
import hmac
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
import requests
import jwt
import pyotp
import qrcode

User = get_user_model()


class SMSVerificationService:
    """Service pour l'envoi et la validation de codes SMS"""
    
    CODE_LENGTH = 6
    CODE_EXPIRY_MINUTES = 10
    MAX_ATTEMPTS = 3
    
    @staticmethod
    def generate_code() -> str:
        """Génère un code de vérification à 6 chiffres"""
        return ''.join(random.choices(string.digits, k=SMSVerificationService.CODE_LENGTH))
    
    @staticmethod
    def _get_cache_key(phone_number: str, prefix: str = 'sms_code') -> str:
        """Génère une clé de cache pour un numéro de téléphone"""
        return f"{prefix}:{phone_number}"
    
    @staticmethod
    def send_verification_code(phone_number: str) -> Dict[str, Any]:
        """
        Envoie un code de vérification par SMS
        
        Args:
            phone_number: Numéro de téléphone au format international
            
        Returns:
            Dict avec status et message
        """
        # Générer le code
        code = SMSVerificationService.generate_code()
        
        # Stocker le code dans Redis avec expiration
        cache_key = SMSVerificationService._get_cache_key(phone_number)
        cache.set(
            cache_key,
            {
                'code': code,
                'attempts': 0,
                'created_at': timezone.now().isoformat()
            },
            timeout=SMSVerificationService.CODE_EXPIRY_MINUTES * 60
        )
        
        # Envoyer le SMS via le gateway
        try:
            message = f"Votre code de vérification Haroo est: {code}. Valide pendant {SMSVerificationService.CODE_EXPIRY_MINUTES} minutes."
            
            # Configuration du gateway SMS (à adapter selon le provider)
            sms_api_key = settings.SMS_GATEWAY_API_KEY
            sender_id = settings.SMS_GATEWAY_SENDER_ID
            
            if not sms_api_key:
                # Mode développement: afficher le code dans les logs
                print(f"[DEV MODE] SMS Code for {phone_number}: {code}")
                return {
                    'status': 'success',
                    'message': 'Code envoyé (mode développement)',
                    'code': code  # Seulement en dev
                }
            
            # Appel API du gateway SMS (exemple générique)
            response = requests.post(
                'https://api.smsgateway.tg/send',  # URL à adapter
                json={
                    'api_key': sms_api_key,
                    'sender': sender_id,
                    'recipient': phone_number,
                    'message': message
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'message': 'Code de vérification envoyé'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Erreur lors de l\'envoi du SMS'
                }
                
        except Exception as e:
            print(f"Erreur envoi SMS: {str(e)}")
            return {
                'status': 'error',
                'message': 'Erreur lors de l\'envoi du SMS'
            }
    
    @staticmethod
    def verify_code(phone_number: str, code: str) -> Dict[str, Any]:
        """
        Vérifie un code de vérification
        
        Args:
            phone_number: Numéro de téléphone
            code: Code à vérifier
            
        Returns:
            Dict avec status et message
        """
        cache_key = SMSVerificationService._get_cache_key(phone_number)
        stored_data = cache.get(cache_key)
        
        if not stored_data:
            return {
                'status': 'error',
                'message': 'Code expiré ou invalide'
            }
        
        # Vérifier le nombre de tentatives
        if stored_data['attempts'] >= SMSVerificationService.MAX_ATTEMPTS:
            cache.delete(cache_key)
            return {
                'status': 'error',
                'message': 'Nombre maximum de tentatives atteint'
            }
        
        # Vérifier le code
        if stored_data['code'] == code:
            cache.delete(cache_key)
            return {
                'status': 'success',
                'message': 'Code vérifié avec succès'
            }
        else:
            # Incrémenter le compteur de tentatives
            stored_data['attempts'] += 1
            cache.set(
                cache_key,
                stored_data,
                timeout=SMSVerificationService.CODE_EXPIRY_MINUTES * 60
            )
            
            remaining = SMSVerificationService.MAX_ATTEMPTS - stored_data['attempts']
            return {
                'status': 'error',
                'message': f'Code incorrect. {remaining} tentative(s) restante(s)'
            }


class JWTAuthService:
    """Service pour la gestion des tokens JWT"""
    
    @staticmethod
    def generate_tokens(user: User) -> Dict[str, str]:
        """
        Génère les tokens d'accès et de rafraîchissement pour un utilisateur
        
        Args:
            user: Instance de l'utilisateur
            
        Returns:
            Dict contenant access_token et refresh_token
        """
        now = datetime.utcnow()
        
        # Payload commun
        base_payload = {
            'user_id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'phone_number': user.phone_number,
        }
        
        # Access token
        access_payload = {
            **base_payload,
            'exp': now + timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME),
            'iat': now,
            'type': 'access'
        }
        
        access_token = jwt.encode(
            access_payload,
            settings.JWT_SECRET_KEY,
            algorithm='HS256'
        )
        
        # Refresh token
        refresh_payload = {
            **base_payload,
            'exp': now + timedelta(seconds=settings.JWT_REFRESH_TOKEN_LIFETIME),
            'iat': now,
            'type': 'refresh'
        }
        
        refresh_token = jwt.encode(
            refresh_payload,
            settings.JWT_SECRET_KEY,
            algorithm='HS256'
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': settings.JWT_ACCESS_TOKEN_LIFETIME
        }
    
    @staticmethod
    def verify_token(token: str, token_type: str = 'access') -> Optional[Dict[str, Any]]:
        """
        Vérifie et décode un token JWT
        
        Args:
            token: Token JWT à vérifier
            token_type: Type de token ('access' ou 'refresh')
            
        Returns:
            Payload du token si valide, None sinon
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=['HS256']
            )
            
            # Vérifier le type de token
            if payload.get('type') != token_type:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Génère un nouveau token d'accès à partir d'un refresh token
        
        Args:
            refresh_token: Token de rafraîchissement
            
        Returns:
            Dict avec le nouveau access_token ou None si invalide
        """
        payload = JWTAuthService.verify_token(refresh_token, token_type='refresh')
        
        if not payload:
            return None
        
        try:
            user = User.objects.get(id=payload['user_id'])
            tokens = JWTAuthService.generate_tokens(user)
            
            return {
                'access_token': tokens['access_token'],
                'expires_in': tokens['expires_in']
            }
        except User.DoesNotExist:
            return None


class RateLimitService:
    """Service pour le rate limiting des tentatives de connexion"""
    
    MAX_ATTEMPTS = 5
    BLOCK_DURATION_MINUTES = 30
    
    @staticmethod
    def _get_cache_key(identifier: str, action: str = 'login') -> str:
        """Génère une clé de cache pour le rate limiting"""
        return f"rate_limit:{action}:{identifier}"
    
    @staticmethod
    def check_rate_limit(identifier: str, action: str = 'login') -> Dict[str, Any]:
        """
        Vérifie si un identifiant (IP ou user) a dépassé la limite
        
        Args:
            identifier: IP ou identifiant utilisateur
            action: Type d'action ('login', 'register', etc.)
            
        Returns:
            Dict avec is_blocked et remaining_attempts
        """
        cache_key = RateLimitService._get_cache_key(identifier, action)
        attempts_data = cache.get(cache_key)
        
        if not attempts_data:
            return {
                'is_blocked': False,
                'remaining_attempts': RateLimitService.MAX_ATTEMPTS
            }
        
        # Vérifier si bloqué
        if attempts_data.get('blocked_until'):
            blocked_until = datetime.fromisoformat(attempts_data['blocked_until'])
            if datetime.utcnow() < blocked_until:
                return {
                    'is_blocked': True,
                    'remaining_attempts': 0,
                    'blocked_until': blocked_until.isoformat()
                }
            else:
                # Le blocage a expiré, réinitialiser
                cache.delete(cache_key)
                return {
                    'is_blocked': False,
                    'remaining_attempts': RateLimitService.MAX_ATTEMPTS
                }
        
        attempts = attempts_data.get('attempts', 0)
        remaining = RateLimitService.MAX_ATTEMPTS - attempts
        
        return {
            'is_blocked': False,
            'remaining_attempts': max(0, remaining)
        }
    
    @staticmethod
    def record_attempt(identifier: str, action: str = 'login', success: bool = False):
        """
        Enregistre une tentative
        
        Args:
            identifier: IP ou identifiant utilisateur
            action: Type d'action
            success: Si la tentative a réussi
        """
        cache_key = RateLimitService._get_cache_key(identifier, action)
        
        if success:
            # Réinitialiser le compteur en cas de succès
            cache.delete(cache_key)
            return
        
        attempts_data = cache.get(cache_key, {'attempts': 0})
        attempts_data['attempts'] += 1
        
        # Bloquer si limite atteinte
        if attempts_data['attempts'] >= RateLimitService.MAX_ATTEMPTS:
            blocked_until = datetime.utcnow() + timedelta(
                minutes=RateLimitService.BLOCK_DURATION_MINUTES
            )
            attempts_data['blocked_until'] = blocked_until.isoformat()
            timeout = RateLimitService.BLOCK_DURATION_MINUTES * 60
        else:
            timeout = 3600  # 1 heure
        
        cache.set(cache_key, attempts_data, timeout=timeout)


class PasswordValidationService:
    """Service pour la validation des mots de passe"""
    
    MIN_LENGTH = 8
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, Any]:
        """
        Valide un mot de passe selon les critères de sécurité
        
        Critères:
        - Minimum 8 caractères
        - Au moins une majuscule
        - Au moins un chiffre
        - Au moins un caractère spécial
        
        Args:
            password: Mot de passe à valider
            
        Returns:
            Dict avec is_valid et errors
        """
        errors = []
        
        if len(password) < PasswordValidationService.MIN_LENGTH:
            errors.append(f"Le mot de passe doit contenir au moins {PasswordValidationService.MIN_LENGTH} caractères")
        
        if not any(c.isupper() for c in password):
            errors.append("Le mot de passe doit contenir au moins une majuscule")
        
        if not any(c.isdigit() for c in password):
            errors.append("Le mot de passe doit contenir au moins un chiffre")
        
        if not any(c in string.punctuation for c in password):
            errors.append("Le mot de passe doit contenir au moins un caractère spécial")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }



class TwoFactorAuthService:
    """
    Service pour l'authentification à deux facteurs (2FA) avec TOTP
    
    Exigences: 25.2
    """
    
    @staticmethod
    def generate_secret() -> str:
        """
        Génère un secret TOTP pour un utilisateur
        
        Returns:
            Secret TOTP encodé en base32
        """
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(user: User, secret: str) -> str:
        """
        Génère un QR code pour configurer l'authentificateur
        
        Args:
            user: Instance de l'utilisateur
            secret: Secret TOTP
            
        Returns:
            QR code encodé en base64
        """
        # Créer l'URI TOTP
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.phone_number,
            issuer_name='Haroo - Plateforme Agricole Togo'
        )
        
        # Générer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Convertir en image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir en base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{qr_code_base64}"
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """
        Vérifie un token TOTP
        
        Args:
            secret: Secret TOTP de l'utilisateur
            token: Token à vérifier (6 chiffres)
            
        Returns:
            True si le token est valide, False sinon
        """
        if not secret or not token:
            return False
        
        try:
            totp = pyotp.TOTP(secret)
            # Vérifier le token avec une fenêtre de tolérance de 1 (30 secondes avant/après)
            return totp.verify(token, valid_window=1)
        except Exception:
            return False
    
    @staticmethod
    def enable_2fa(user: User, token: str) -> Dict[str, Any]:
        """
        Active le 2FA pour un utilisateur après vérification du token
        
        Args:
            user: Instance de l'utilisateur
            token: Token TOTP pour vérification
            
        Returns:
            Dict avec status et message
        """
        if not user.two_factor_secret:
            return {
                'status': 'error',
                'message': 'Aucun secret 2FA configuré. Veuillez d\'abord configurer le 2FA.'
            }
        
        # Vérifier le token
        if not TwoFactorAuthService.verify_token(user.two_factor_secret, token):
            return {
                'status': 'error',
                'message': 'Token invalide. Veuillez vérifier le code dans votre application d\'authentification.'
            }
        
        # Activer le 2FA
        user.two_factor_enabled = True
        user.save(update_fields=['two_factor_enabled'])
        
        # Générer des codes de secours
        backup_codes = TwoFactorAuthService._generate_backup_codes(user)
        
        return {
            'status': 'success',
            'message': '2FA activé avec succès',
            'backup_codes': backup_codes
        }
    
    @staticmethod
    def disable_2fa(user: User, password: str) -> Dict[str, Any]:
        """
        Désactive le 2FA pour un utilisateur
        
        Args:
            user: Instance de l'utilisateur
            password: Mot de passe pour confirmation
            
        Returns:
            Dict avec status et message
        """
        # Vérifier le mot de passe
        if not user.check_password(password):
            return {
                'status': 'error',
                'message': 'Mot de passe incorrect'
            }
        
        # Désactiver le 2FA
        user.two_factor_enabled = False
        user.two_factor_secret = None
        user.save(update_fields=['two_factor_enabled', 'two_factor_secret'])
        
        # Supprimer les codes de secours
        cache_key = f"2fa_backup_codes:{user.id}"
        cache.delete(cache_key)
        
        return {
            'status': 'success',
            'message': '2FA désactivé avec succès'
        }
    
    @staticmethod
    def setup_2fa(user: User) -> Dict[str, Any]:
        """
        Configure le 2FA pour un utilisateur (génère secret et QR code)
        
        Args:
            user: Instance de l'utilisateur
            
        Returns:
            Dict avec secret et qr_code
        """
        # Générer un nouveau secret
        secret = TwoFactorAuthService.generate_secret()
        
        # Sauvegarder le secret (mais ne pas activer le 2FA encore)
        user.two_factor_secret = secret
        user.save(update_fields=['two_factor_secret'])
        
        # Générer le QR code
        qr_code = TwoFactorAuthService.generate_qr_code(user, secret)
        
        return {
            'status': 'success',
            'secret': secret,
            'qr_code': qr_code,
            'message': 'Scannez le QR code avec votre application d\'authentification (Google Authenticator, Authy, etc.)'
        }
    
    @staticmethod
    def _generate_backup_codes(user: User, count: int = 10) -> list:
        """
        Génère des codes de secours pour le 2FA
        
        Args:
            user: Instance de l'utilisateur
            count: Nombre de codes à générer
            
        Returns:
            Liste de codes de secours
        """
        backup_codes = []
        for _ in range(count):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            backup_codes.append(code)
        
        # Stocker les codes hashés dans le cache (valides 1 an)
        hashed_codes = [hashlib.sha256(code.encode()).hexdigest() for code in backup_codes]
        cache_key = f"2fa_backup_codes:{user.id}"
        cache.set(cache_key, hashed_codes, timeout=365 * 24 * 60 * 60)
        
        return backup_codes
    
    @staticmethod
    def verify_backup_code(user: User, code: str) -> bool:
        """
        Vérifie et consomme un code de secours
        
        Args:
            user: Instance de l'utilisateur
            code: Code de secours à vérifier
            
        Returns:
            True si le code est valide, False sinon
        """
        cache_key = f"2fa_backup_codes:{user.id}"
        backup_codes = cache.get(cache_key, [])
        
        if not backup_codes:
            return False
        
        # Hasher le code fourni
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Vérifier si le code existe
        if code_hash in backup_codes:
            # Retirer le code utilisé
            backup_codes.remove(code_hash)
            cache.set(cache_key, backup_codes, timeout=365 * 24 * 60 * 60)
            return True
        
        return False
    
    @staticmethod
    def require_2fa_for_institution(user: User) -> bool:
        """
        Vérifie si le 2FA est obligatoire pour un utilisateur
        
        Args:
            user: Instance de l'utilisateur
            
        Returns:
            True si le 2FA est obligatoire, False sinon
        """
        # Le 2FA est obligatoire pour les comptes institutionnels
        return user.user_type == 'INSTITUTION'
    
    @staticmethod
    def check_2fa_required(user: User) -> Dict[str, Any]:
        """
        Vérifie si le 2FA est requis et configuré pour un utilisateur
        
        Args:
            user: Instance de l'utilisateur
            
        Returns:
            Dict avec required, enabled, et message
        """
        required = TwoFactorAuthService.require_2fa_for_institution(user)
        enabled = user.two_factor_enabled
        
        if required and not enabled:
            return {
                'required': True,
                'enabled': False,
                'message': 'Le 2FA est obligatoire pour les comptes institutionnels. Veuillez l\'activer.'
            }
        
        return {
            'required': required,
            'enabled': enabled,
            'message': 'OK'
        }


class ValidationWorkflowService:
    """
    Service pour gérer le workflow de validation administrative des agronomes
    
    Exigences: 7.5, 7.6
    
    Workflow:
    1. Admin vérifie les documents justificatifs
    2. Si OK: Statut VALIDE + Badge Agronome_Validé
    3. Si KO: Statut REJETE + Notification avec motif
    """
    
    @staticmethod
    def validate_agronomist(agronome_profile, admin_user, approved: bool, motif_rejet: str = None) -> Dict[str, Any]:
        """
        Valider ou rejeter une demande d'agronome
        
        Args:
            agronome_profile: Le profil agronome à valider
            admin_user: L'administrateur qui effectue la validation
            approved: True pour valider, False pour rejeter
            motif_rejet: Motif du rejet (requis si approved=False)
            
        Returns:
            Dict avec le statut et les informations de validation
            
        Exigences: 7.5, 7.6
        """
        from django.utils import timezone
        from django.db import transaction
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Vérifier que le profil est en attente de validation
        if agronome_profile.statut_validation != 'EN_ATTENTE':
            return {
                'success': False,
                'error': f'Le profil est déjà {agronome_profile.get_statut_validation_display()}'
            }
        
        # Vérifier que l'utilisateur est un administrateur
        if not admin_user.is_staff and not admin_user.is_superuser:
            return {
                'success': False,
                'error': 'Seuls les administrateurs peuvent valider les agronomes'
            }
        
        # Si rejet, vérifier qu'un motif est fourni
        if not approved and not motif_rejet:
            return {
                'success': False,
                'error': 'Un motif de rejet est requis'
            }
        
        try:
            with transaction.atomic():
                if approved:
                    # Validation: Statut VALIDE + Badge (Exigence 7.5)
                    agronome_profile.statut_validation = 'VALIDE'
                    agronome_profile.badge_valide = True
                    agronome_profile.date_validation = timezone.now()
                    agronome_profile.motif_rejet = None
                    agronome_profile.save()
                    
                    # Envoyer notification de validation
                    ValidationWorkflowService._send_validation_notification(
                        agronome_profile,
                        approved=True
                    )
                    
                    logger.info(
                        f"Agronome validé: {agronome_profile.user.username} par {admin_user.username}"
                    )
                    
                    return {
                        'success': True,
                        'message': 'Agronome validé avec succès',
                        'agronome': {
                            'id': agronome_profile.user.id,
                            'username': agronome_profile.user.username,
                            'statut_validation': agronome_profile.statut_validation,
                            'badge_valide': agronome_profile.badge_valide,
                            'date_validation': agronome_profile.date_validation.isoformat()
                        }
                    }
                else:
                    # Rejet: Statut REJETE + Notification avec motif (Exigence 7.6)
                    agronome_profile.statut_validation = 'REJETE'
                    agronome_profile.badge_valide = False
                    agronome_profile.motif_rejet = motif_rejet
                    agronome_profile.date_validation = timezone.now()
                    agronome_profile.save()
                    
                    # Envoyer notification de rejet avec motif
                    ValidationWorkflowService._send_validation_notification(
                        agronome_profile,
                        approved=False,
                        motif_rejet=motif_rejet
                    )
                    
                    logger.info(
                        f"Agronome rejeté: {agronome_profile.user.username} par {admin_user.username} - "
                        f"Motif: {motif_rejet}"
                    )
                    
                    return {
                        'success': True,
                        'message': 'Demande rejetée',
                        'agronome': {
                            'id': agronome_profile.user.id,
                            'username': agronome_profile.user.username,
                            'statut_validation': agronome_profile.statut_validation,
                            'badge_valide': agronome_profile.badge_valide,
                            'motif_rejet': agronome_profile.motif_rejet,
                            'date_validation': agronome_profile.date_validation.isoformat()
                        }
                    }
                    
        except Exception as e:
            logger.error(f"Erreur lors de la validation de l'agronome: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur lors de la validation: {str(e)}'
            }
    
    @staticmethod
    def _send_validation_notification(agronome_profile, approved: bool, motif_rejet: str = None):
        """
        Envoyer une notification de validation/rejet à l'agronome
        
        Args:
            agronome_profile: Le profil agronome
            approved: True si validé, False si rejeté
            motif_rejet: Motif du rejet (si applicable)
            
        Exigences: 7.5, 7.6
        """
        import logging
        
        logger = logging.getLogger(__name__)
        
        user = agronome_profile.user
        
        if approved:
            # Notification de validation
            message = (
                f"Félicitations {user.first_name}! Votre profil d'agronome a été validé. "
                f"Vous avez maintenant le badge Agronome_Validé et êtes visible dans l'annuaire."
            )
            sms_message = f"Votre profil agronome a ete valide. Badge Agronome_Valide attribue."
        else:
            # Notification de rejet avec motif (Exigence 7.6)
            message = (
                f"Bonjour {user.first_name}, votre demande de validation en tant qu'agronome "
                f"a été rejetée. Motif: {motif_rejet}"
            )
            sms_message = f"Demande agronome rejetee. Motif: {motif_rejet[:100]}"
        
        # Envoyer SMS (limité à 160 caractères)
        try:
            # Tronquer le message SMS si nécessaire
            if len(sms_message) > 160:
                sms_message = sms_message[:157] + "..."
            
            # TODO: Intégrer avec le service SMS réel
            # Pour l'instant, on log simplement
            logger.info(f"SMS à envoyer à {user.phone_number}: {sms_message}")
            
            # Dans une implémentation complète, on utiliserait:
            # SMSVerificationService.send_sms(user.phone_number, sms_message)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification SMS: {str(e)}")
        
        # TODO: Envoyer email si disponible
        if user.email:
            logger.info(f"Email à envoyer à {user.email}: {message}")
    
    @staticmethod
    def get_pending_validations() -> Dict[str, Any]:
        """
        Récupérer la liste des agronomes en attente de validation
        
        Returns:
            Dict avec la liste des profils en attente
        """
        from .models import AgronomeProfile
        
        pending_profiles = AgronomeProfile.objects.filter(
            statut_validation='EN_ATTENTE'
        ).select_related('user', 'canton_rattachement').order_by('user__date_joined')
        
        profiles_data = []
        for profile in pending_profiles:
            profiles_data.append({
                'id': profile.user.id,
                'username': profile.user.username,
                'first_name': profile.user.first_name,
                'last_name': profile.user.last_name,
                'email': profile.user.email,
                'phone_number': profile.user.phone_number,
                'canton_rattachement': {
                    'id': profile.canton_rattachement.id,
                    'nom': profile.canton_rattachement.nom
                },
                'specialisations': profile.specialisations,
                'date_inscription': profile.user.date_joined.isoformat(),
                'nombre_documents': profile.documents_justificatifs.count()
            })
        
        return {
            'success': True,
            'count': len(profiles_data),
            'profiles': profiles_data
        }



class FarmVerificationService:
    """
    Service pour gérer le workflow de validation des exploitations agricoles
    
    Exigences: 10.4, 10.5, 10.6
    
    Workflow:
    1. Admin vérifie les documents justificatifs et la cohérence GPS/superficie
    2. Si OK: Statut VERIFIE + Déblocage fonctionnalités premium
    3. Si KO: Statut REJETE + Notification avec motif
    """
    
    @staticmethod
    def verify_farm(exploitant_profile, admin_user, approved: bool, motif_rejet: str = None) -> Dict[str, Any]:
        """
        Valider ou rejeter une demande de vérification d'exploitation
        
        Args:
            exploitant_profile: Le profil exploitant à vérifier
            admin_user: L'administrateur qui effectue la vérification
            approved: True pour valider, False pour rejeter
            motif_rejet: Motif du rejet (requis si approved=False)
            
        Returns:
            Dict avec le statut et les informations de vérification
            
        Exigences: 10.4, 10.5, 10.6
        """
        from django.utils import timezone
        from django.db import transaction
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Vérifier que le profil est en attente de vérification
        if exploitant_profile.statut_verification != 'EN_ATTENTE':
            return {
                'success': False,
                'error': f'Le profil est déjà {exploitant_profile.get_statut_verification_display()}'
            }
        
        # Vérifier que l'utilisateur est un administrateur
        if not admin_user.is_staff and not admin_user.is_superuser:
            return {
                'success': False,
                'error': 'Seuls les administrateurs peuvent vérifier les exploitations'
            }
        
        # Si rejet, vérifier qu'un motif est fourni
        if not approved and not motif_rejet:
            return {
                'success': False,
                'error': 'Un motif de rejet est requis'
            }
        
        try:
            with transaction.atomic():
                if approved:
                    # Validation: Statut VERIFIE + Déblocage fonctionnalités premium (Exigence 10.5)
                    exploitant_profile.statut_verification = 'VERIFIE'
                    exploitant_profile.date_verification = timezone.now()
                    exploitant_profile.motif_rejet = None
                    exploitant_profile.save()
                    
                    # Envoyer notification de validation
                    FarmVerificationService._send_verification_notification(
                        exploitant_profile,
                        approved=True
                    )
                    
                    logger.info(
                        f"Exploitation vérifiée: {exploitant_profile.user.username} "
                        f"({exploitant_profile.superficie_totale}ha) par {admin_user.username}"
                    )
                    
                    return {
                        'success': True,
                        'message': 'Exploitation vérifiée avec succès. Les fonctionnalités premium sont maintenant débloquées.',
                        'exploitant': {
                            'id': exploitant_profile.user.id,
                            'username': exploitant_profile.user.username,
                            'statut_verification': exploitant_profile.statut_verification,
                            'date_verification': exploitant_profile.date_verification.isoformat(),
                            'superficie_totale': str(exploitant_profile.superficie_totale),
                            'premium_features_unlocked': True
                        }
                    }
                else:
                    # Rejet: Statut REJETE + Notification avec motif (Exigence 10.6)
                    exploitant_profile.statut_verification = 'REJETE'
                    exploitant_profile.motif_rejet = motif_rejet
                    exploitant_profile.date_verification = timezone.now()
                    exploitant_profile.save()
                    
                    # Envoyer notification de rejet avec motif
                    FarmVerificationService._send_verification_notification(
                        exploitant_profile,
                        approved=False,
                        motif_rejet=motif_rejet
                    )
                    
                    logger.info(
                        f"Exploitation rejetée: {exploitant_profile.user.username} par {admin_user.username} - "
                        f"Motif: {motif_rejet}"
                    )
                    
                    return {
                        'success': True,
                        'message': 'Demande rejetée',
                        'exploitant': {
                            'id': exploitant_profile.user.id,
                            'username': exploitant_profile.user.username,
                            'statut_verification': exploitant_profile.statut_verification,
                            'motif_rejet': exploitant_profile.motif_rejet,
                            'date_verification': exploitant_profile.date_verification.isoformat()
                        }
                    }
                    
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'exploitation: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur lors de la vérification: {str(e)}'
            }
    
    @staticmethod
    def _send_verification_notification(exploitant_profile, approved: bool, motif_rejet: str = None):
        """
        Envoyer une notification de validation/rejet à l'exploitant
        
        Args:
            exploitant_profile: Le profil exploitant
            approved: True si vérifié, False si rejeté
            motif_rejet: Motif du rejet (si applicable)
            
        Exigences: 10.5, 10.6
        """
        import logging
        
        logger = logging.getLogger(__name__)
        
        user = exploitant_profile.user
        
        if approved:
            # Notification de vérification (Exigence 10.5)
            message = (
                f"Félicitations {user.first_name}! Votre exploitation de {exploitant_profile.superficie_totale}ha "
                f"a été vérifiée. Vous avez maintenant accès aux fonctionnalités premium: "
                f"recrutement d'agronomes et d'ouvriers, préventes agricoles, analyses de marché, "
                f"optimisation logistique et recommandations de cultures."
            )
            sms_message = (
                f"Votre exploitation a ete verifiee. Acces aux fonctionnalites premium active."
            )
        else:
            # Notification de rejet avec motif (Exigence 10.6)
            message = (
                f"Bonjour {user.first_name}, votre demande de vérification d'exploitation "
                f"a été rejetée. Motif: {motif_rejet}"
            )
            sms_message = f"Demande exploitation rejetee. Motif: {motif_rejet[:100]}"
        
        # Envoyer SMS (limité à 160 caractères)
        try:
            # Tronquer le message SMS si nécessaire
            if len(sms_message) > 160:
                sms_message = sms_message[:157] + "..."
            
            # TODO: Intégrer avec le service SMS réel
            # Pour l'instant, on log simplement
            logger.info(f"SMS à envoyer à {user.phone_number}: {sms_message}")
            
            # Dans une implémentation complète, on utiliserait:
            # SMSVerificationService.send_sms(user.phone_number, sms_message)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification SMS: {str(e)}")
        
        # TODO: Envoyer email si disponible
        if user.email:
            logger.info(f"Email à envoyer à {user.email}: {message}")
    
    @staticmethod
    def get_pending_verifications() -> Dict[str, Any]:
        """
        Récupérer la liste des exploitations en attente de vérification
        
        Returns:
            Dict avec la liste des profils en attente
        """
        from .models import ExploitantProfile
        
        pending_profiles = ExploitantProfile.objects.filter(
            statut_verification='EN_ATTENTE'
        ).select_related(
            'user',
            'canton_principal',
            'canton_principal__prefecture',
            'canton_principal__prefecture__region'
        ).prefetch_related('documents_verification').order_by('user__date_joined')
        
        profiles_data = []
        for profile in pending_profiles:
            profiles_data.append({
                'id': profile.user.id,
                'username': profile.user.username,
                'first_name': profile.user.first_name,
                'last_name': profile.user.last_name,
                'email': profile.user.email,
                'phone_number': profile.user.phone_number,
                'superficie_totale': str(profile.superficie_totale),
                'canton_principal': {
                    'id': profile.canton_principal.id,
                    'nom': profile.canton_principal.nom,
                    'prefecture': {
                        'id': profile.canton_principal.prefecture.id,
                        'nom': profile.canton_principal.prefecture.nom,
                        'region': {
                            'id': profile.canton_principal.prefecture.region.id,
                            'nom': profile.canton_principal.prefecture.region.nom
                        }
                    }
                },
                'cultures_actuelles': profile.cultures_actuelles,
                'date_demande': profile.user.date_joined.isoformat(),
                'nombre_documents': profile.documents_verification.count()
            })
        
        return {
            'success': True,
            'count': len(profiles_data),
            'profiles': profiles_data
        }
