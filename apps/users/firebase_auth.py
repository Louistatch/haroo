"""
Vérification des tokens Firebase Auth.
Vérifie un ID token Firebase via l'API publique Google (sans credentials fichier).
"""
import logging
import requests

logger = logging.getLogger(__name__)

FIREBASE_PROJECT_ID = 'digitnew-b8313'
GOOGLE_CERTS_URL = 'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'
GOOGLE_TOKEN_INFO_URL = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo'
FIREBASE_VERIFY_URL = f'https://identitytoolkit.googleapis.com/v1/accounts:lookup'
FIREBASE_API_KEY = 'AIzaSyA8bIraGpvVsHWCDWOvDRbeTEzQd8ozQcw'


def verify_firebase_token(id_token: str) -> dict:
    """
    Vérifie un ID token Firebase Auth via l'API Google Identity Toolkit.
    Pas besoin de service account / credentials fichier.
    """
    try:
        resp = requests.post(
            f"{FIREBASE_VERIFY_URL}?key={FIREBASE_API_KEY}",
            json={"idToken": id_token},
            timeout=10,
        )
    except requests.RequestException as e:
        logger.error("Erreur réseau Firebase: %s", e)
        raise ValueError(f"Impossible de contacter Firebase: {e}")

    if resp.status_code != 200:
        error_msg = resp.json().get('error', {}).get('message', 'Token invalide')
        logger.error("Firebase token verification failed: %s", error_msg)
        raise ValueError(f"Token Firebase invalide: {error_msg}")

    data = resp.json()
    users = data.get('users', [])
    if not users:
        raise ValueError("Utilisateur introuvable dans Firebase.")

    user = users[0]
    email = user.get('email', '')
    if not email:
        raise ValueError("Email introuvable dans le token Firebase.")

    return {
        "email": email,
        "name": user.get('displayName', ''),
        "image": user.get('photoUrl', ''),
        "firebase_uid": user.get('localId', ''),
        "email_verified": user.get('emailVerified', False),
    }
