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
    """
    try:
        resp = requests.get(
            f"{NEON_AUTH_URL}/get-session",
            headers={"Authorization": f"Bearer {session_token}"},
            timeout=10,
        )
    except requests.RequestException as e:
        logger.error("Erreur réseau Neon Auth: %s", e)
        raise ValueError(f"Impossible de contacter Neon Auth: {e}")

    if resp.status_code == 401:
        raise ValueError("Session Neon Auth expirée ou invalide.")
    if resp.status_code != 200:
        raise ValueError(f"Neon Auth a retourné HTTP {resp.status_code}.")

    data = resp.json()
    if not data:
        raise ValueError("Session Neon Auth invalide ou expirée.")
    user = data.get("user") or {}
    if not user:
        raise ValueError("Aucun utilisateur dans la session Neon Auth.")

    email = user.get("email", "")
    if not email:
        raise ValueError("Email introuvable dans la session Neon Auth.")

    return {
        "email": email,
        "name": user.get("name", ""),
        "image": user.get("image", ""),
        "neon_id": user.get("id", ""),
    }
