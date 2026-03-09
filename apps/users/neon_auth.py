"""
Validation des sessions Neon Auth (Better Auth)
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

NEON_AUTH_URL = (
    "https://ep-muddy-salad-aljfiixs.neonauth.c-3.eu-central-1.aws.neon.tech"
    "/neondb/auth"
)


def verify_neon_session(session_token: str) -> dict:
    """
    Vérifie un token de session Neon Auth et retourne les infos utilisateur.
    Lève ValueError si la session est invalide.
    
    Essaie d'abord comme Bearer token, puis comme cookie de session.
    """
    # Try as Bearer token first
    for auth_method in ["bearer", "cookie"]:
        try:
            if auth_method == "bearer":
                resp = requests.get(
                    f"{NEON_AUTH_URL}/get-session",
                    headers={"Authorization": f"Bearer {session_token}"},
                    timeout=10,
                )
            else:
                cookie_name = "__Secure-neonauth.session_token"
                resp = requests.get(
                    f"{NEON_AUTH_URL}/get-session",
                    cookies={cookie_name: session_token},
                    timeout=10,
                )

            if resp.status_code == 200:
                data = resp.json()
                user = (data or {}).get("user") or {}
                email = user.get("email", "")
                if email:
                    return {
                        "email": email,
                        "name": user.get("name", ""),
                        "image": user.get("image", ""),
                        "neon_id": user.get("id", ""),
                    }
        except requests.RequestException as e:
            logger.error("Erreur réseau Neon Auth (%s): %s", auth_method, e)
            continue

    raise ValueError("Session Neon Auth expirée ou invalide.")
