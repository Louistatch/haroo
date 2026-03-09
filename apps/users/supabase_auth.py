"""
Validation des tokens Supabase Auth.
Vérifie un access_token Supabase et retourne les infos utilisateur.
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def verify_supabase_token(access_token: str) -> dict:
    """
    Vérifie un access_token Supabase Auth via l'endpoint /auth/v1/user.
    Lève ValueError si le token est invalide.
    """
    supabase_url = getattr(settings, 'SUPABASE_URL', '') or ''
    if not supabase_url:
        raise ValueError("SUPABASE_URL non configuré.")

    try:
        resp = requests.get(
            f"{supabase_url}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": getattr(settings, 'SUPABASE_ANON_KEY', '') or getattr(settings, 'SUPABASE_SERVICE_KEY', ''),
            },
            timeout=10,
        )
    except requests.RequestException as e:
        logger.error("Erreur réseau Supabase Auth: %s", e)
        raise ValueError(f"Impossible de contacter Supabase: {e}")

    if resp.status_code == 401:
        raise ValueError("Token Supabase expiré ou invalide.")
    if resp.status_code != 200:
        raise ValueError(f"Supabase Auth a retourné HTTP {resp.status_code}.")

    data = resp.json()
    email = data.get("email", "")
    if not email:
        raise ValueError("Email introuvable dans le token Supabase.")

    user_meta = data.get("user_metadata", {})
    return {
        "email": email,
        "name": user_meta.get("full_name", user_meta.get("name", "")),
        "image": user_meta.get("avatar_url", user_meta.get("picture", "")),
        "supabase_id": data.get("id", ""),
    }
