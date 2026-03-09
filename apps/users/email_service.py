"""
Service d'envoi d'emails pour l'authentification
- Vérification d'email
- Réinitialisation de mot de passe
"""
import secrets
import logging
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)

FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')


class EmailVerificationService:
    """Gestion des tokens de vérification d'email"""

    TOKEN_LENGTH = 64
    TOKEN_EXPIRY_HOURS = 24
    CACHE_PREFIX = 'email_verify'

    @classmethod
    def generate_token(cls, user_id: int, email: str) -> str:
        token = secrets.token_urlsafe(cls.TOKEN_LENGTH)
        cache_key = f"{cls.CACHE_PREFIX}:{token}"
        cache.set(cache_key, {
            'user_id': user_id,
            'email': email,
        }, timeout=cls.TOKEN_EXPIRY_HOURS * 3600)
        return token

    @classmethod
    def verify_token(cls, token: str) -> dict | None:
        cache_key = f"{cls.CACHE_PREFIX}:{token}"
        data = cache.get(cache_key)
        if data:
            cache.delete(cache_key)
        return data

    @classmethod
    def send_verification_email(cls, user) -> bool:
        token = cls.generate_token(user.id, user.email)
        verify_url = f"{FRONTEND_URL}/verify-email?token={token}"

        subject = "Haroo — Vérifiez votre adresse email"
        message = (
            f"Bonjour {user.first_name or user.username},\n\n"
            f"Bienvenue sur Haroo ! Veuillez vérifier votre adresse email "
            f"en cliquant sur le lien ci-dessous :\n\n"
            f"{verify_url}\n\n"
            f"Ce lien est valide pendant {cls.TOKEN_EXPIRY_HOURS} heures.\n\n"
            f"Si vous n'avez pas créé de compte sur Haroo, ignorez cet email.\n\n"
            f"L'équipe Haroo"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info("Email de vérification envoyé à %s", user.email)
            return True
        except Exception as e:
            logger.error("Erreur envoi email vérification à %s: %s", user.email, e)
            return False


class PasswordResetService:
    """Gestion des tokens de réinitialisation de mot de passe"""

    TOKEN_LENGTH = 64
    TOKEN_EXPIRY_HOURS = 1
    CACHE_PREFIX = 'pwd_reset'

    @classmethod
    def generate_token(cls, user_id: int, email: str) -> str:
        token = secrets.token_urlsafe(cls.TOKEN_LENGTH)
        cache_key = f"{cls.CACHE_PREFIX}:{token}"
        cache.set(cache_key, {
            'user_id': user_id,
            'email': email,
        }, timeout=cls.TOKEN_EXPIRY_HOURS * 3600)
        return token

    @classmethod
    def verify_token(cls, token: str) -> dict | None:
        cache_key = f"{cls.CACHE_PREFIX}:{token}"
        return cache.get(cache_key)

    @classmethod
    def consume_token(cls, token: str) -> dict | None:
        cache_key = f"{cls.CACHE_PREFIX}:{token}"
        data = cache.get(cache_key)
        if data:
            cache.delete(cache_key)
        return data

    @classmethod
    def send_reset_email(cls, user) -> bool:
        token = cls.generate_token(user.id, user.email)
        reset_url = f"{FRONTEND_URL}/reset-password?token={token}"

        subject = "Haroo — Réinitialisation de votre mot de passe"
        message = (
            f"Bonjour {user.first_name or user.username},\n\n"
            f"Vous avez demandé la réinitialisation de votre mot de passe.\n"
            f"Cliquez sur le lien ci-dessous pour choisir un nouveau mot de passe :\n\n"
            f"{reset_url}\n\n"
            f"Ce lien est valide pendant {cls.TOKEN_EXPIRY_HOURS} heure(s).\n\n"
            f"Si vous n'avez pas fait cette demande, ignorez cet email.\n\n"
            f"L'équipe Haroo"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info("Email de réinitialisation envoyé à %s", user.email)
            return True
        except Exception as e:
            logger.error("Erreur envoi email reset à %s: %s", user.email, e)
            return False
