"""
Vues pour l'authentification et la gestion des utilisateurs
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, get_user_model
from django.views.decorators.csrf import csrf_exempt

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    VerifySMSSerializer,
    RefreshTokenSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer
)
from .services import (
    SMSVerificationService,
    JWTAuthService,
    RateLimitService
)

User = get_user_model()


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Inscription d'un nouvel utilisateur
    
    Étapes:
    1. Valider les données
    2. Créer l'utilisateur
    3. Envoyer le code de vérification SMS
    4. Retourner les informations utilisateur
    """
    # Vérifier le rate limiting par IP
    client_ip = get_client_ip(request)
    rate_limit = RateLimitService.check_rate_limit(client_ip, action='register')
    
    if rate_limit['is_blocked']:
        return Response({
            'error': 'Trop de tentatives. Veuillez réessayer plus tard.',
            'blocked_until': rate_limit.get('blocked_until')
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    serializer = RegisterSerializer(data=request.data)
    
    if not serializer.is_valid():
        # Enregistrer la tentative échouée
        RateLimitService.record_attempt(client_ip, action='register', success=False)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Créer l'utilisateur
        user = serializer.save()
        
        # Envoyer le code de vérification SMS
        sms_result = SMSVerificationService.send_verification_code(user.phone_number)
        
        # Enregistrer la tentative réussie
        RateLimitService.record_attempt(client_ip, action='register', success=True)
        
        return Response({
            'message': 'Inscription réussie. Un code de vérification a été envoyé par SMS.',
            'user': UserSerializer(user).data,
            'sms_sent': sms_result['status'] == 'success'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        RateLimitService.record_attempt(client_ip, action='register', success=False)
        return Response({
            'error': 'Erreur lors de l\'inscription',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Connexion d'un utilisateur
    
    Retourne les tokens JWT si les identifiants sont corrects
    Si le 2FA est activé, retourne un indicateur pour demander le token 2FA
    """
    from .services import TwoFactorAuthService
    
    # Vérifier le rate limiting par IP
    client_ip = get_client_ip(request)
    rate_limit = RateLimitService.check_rate_limit(client_ip, action='login')
    
    if rate_limit['is_blocked']:
        return Response({
            'error': 'Compte temporairement bloqué suite à trop de tentatives échouées.',
            'blocked_until': rate_limit.get('blocked_until')
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    password = serializer.validated_data['password']
    
    try:
        # Récupérer l'utilisateur par numéro de téléphone
        user = User.objects.get(phone_number=phone_number)
        
        # Vérifier le mot de passe
        if not user.check_password(password):
            RateLimitService.record_attempt(client_ip, action='login', success=False)
            RateLimitService.record_attempt(phone_number, action='login', success=False)
            
            remaining = RateLimitService.check_rate_limit(phone_number, action='login')
            
            return Response({
                'error': 'Identifiants incorrects',
                'remaining_attempts': remaining['remaining_attempts']
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Vérifier si le compte est actif
        if not user.is_active:
            return Response({
                'error': 'Ce compte a été désactivé'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Vérifier si le 2FA est activé
        if user.two_factor_enabled:
            # Ne pas générer les tokens JWT, demander le token 2FA
            RateLimitService.record_attempt(client_ip, action='login', success=True)
            RateLimitService.record_attempt(phone_number, action='login', success=True)
            
            return Response({
                'message': 'Identifiants corrects. Veuillez fournir le code 2FA.',
                'requires_2fa': True,
                'phone_number': phone_number
            }, status=status.HTTP_200_OK)
        
        # Vérifier si le 2FA est obligatoire mais pas activé
        if TwoFactorAuthService.require_2fa_for_institution(user):
            return Response({
                'error': 'Le 2FA est obligatoire pour les comptes institutionnels. Veuillez l\'activer avant de vous connecter.',
                'requires_2fa_setup': True
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Générer les tokens JWT
        tokens = JWTAuthService.generate_tokens(user)
        
        # Créer la session dans Redis
        from .session_service import SessionManagementService
        
        client_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        SessionManagementService.create_session(
            user_id=user.id,
            token=tokens['access_token'],
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        # Enregistrer la tentative réussie
        RateLimitService.record_attempt(client_ip, action='login', success=True)
        RateLimitService.record_attempt(phone_number, action='login', success=True)
        
        return Response({
            'message': 'Connexion réussie',
            'user': UserSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        RateLimitService.record_attempt(client_ip, action='login', success=False)
        
        return Response({
            'error': 'Identifiants incorrects'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_sms(request):
    """
    Vérification du code SMS
    
    Marque le numéro de téléphone comme vérifié
    """
    serializer = VerifySMSSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    code = serializer.validated_data['code']
    
    # Vérifier le code
    result = SMSVerificationService.verify_code(phone_number, code)
    
    if result['status'] == 'success':
        try:
            # Marquer le téléphone comme vérifié
            user = User.objects.get(phone_number=phone_number)
            user.phone_verified = True
            user.save()
            
            # Générer les tokens JWT
            tokens = JWTAuthService.generate_tokens(user)
            
            # Créer la session dans Redis
            from .session_service import SessionManagementService
            
            client_ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            SessionManagementService.create_session(
                user_id=user.id,
                token=tokens['access_token'],
                ip_address=client_ip,
                user_agent=user_agent
            )
            
            return Response({
                'message': 'Téléphone vérifié avec succès',
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'error': 'Utilisateur non trouvé'
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({
            'error': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_sms_code(request):
    """
    Renvoie un code de vérification SMS
    """
    phone_number = request.data.get('phone_number')
    
    if not phone_number:
        return Response({
            'error': 'Numéro de téléphone requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(phone_number=phone_number)
        
        if user.phone_verified:
            return Response({
                'error': 'Ce numéro est déjà vérifié'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Envoyer le code
        result = SMSVerificationService.send_verification_code(phone_number)
        
        if result['status'] == 'success':
            return Response({
                'message': 'Code de vérification renvoyé'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result['message']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Rafraîchit le token d'accès
    """
    serializer = RefreshTokenSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    refresh_token = serializer.validated_data['refresh_token']
    
    # Générer un nouveau token d'accès
    result = JWTAuthService.refresh_access_token(refresh_token)
    
    if result:
        return Response({
            'access_token': result['access_token'],
            'expires_in': result['expires_in']
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Token de rafraîchissement invalide ou expiré'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def manage_profile(request):
    """
    GET: Récupère les informations complètes de l'utilisateur connecté avec son profil
    PATCH: Met à jour le profil de l'utilisateur connecté
    
    Exigences: 2.5, 31.1, 31.3
    """
    if request.method == 'GET':
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        # Utiliser le serializer complet pour gérer les profils
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profil mis à jour avec succès',
                'user': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change le mot de passe de l'utilisateur connecté
    """
    serializer = ChangePasswordSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    # Vérifier l'ancien mot de passe
    if not user.check_password(serializer.validated_data['old_password']):
        return Response({
            'error': 'Mot de passe actuel incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Changer le mot de passe
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    
    return Response({
        'message': 'Mot de passe changé avec succès'
    }, status=status.HTTP_200_OK)



# ============================================
# Endpoints 2FA (Authentification à deux facteurs)
# Exigences: 25.2
# ============================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setup_2fa(request):
    """
    Configure le 2FA pour l'utilisateur connecté
    
    Génère un secret TOTP et un QR code à scanner avec une application d'authentification
    
    Exigences: 25.2
    """
    from .services import TwoFactorAuthService
    
    user = request.user
    
    # Vérifier si le 2FA est déjà activé
    if user.two_factor_enabled:
        return Response({
            'error': 'Le 2FA est déjà activé pour ce compte'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Configurer le 2FA
    result = TwoFactorAuthService.setup_2fa(user)
    
    return Response({
        'message': result['message'],
        'secret': result['secret'],
        'qr_code': result['qr_code'],
        'instructions': [
            '1. Installez une application d\'authentification (Google Authenticator, Authy, Microsoft Authenticator, etc.)',
            '2. Scannez le QR code avec l\'application',
            '3. Entrez le code à 6 chiffres généré par l\'application pour activer le 2FA'
        ]
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """
    Active le 2FA après vérification du token
    
    Exigences: 25.2
    """
    from .serializers import Enable2FASerializer
    from .services import TwoFactorAuthService
    
    serializer = Enable2FASerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    token = serializer.validated_data['token']
    
    # Activer le 2FA
    result = TwoFactorAuthService.enable_2fa(user, token)
    
    if result['status'] == 'success':
        return Response({
            'message': result['message'],
            'backup_codes': result['backup_codes'],
            'warning': 'Conservez ces codes de secours dans un endroit sûr. Ils vous permettront de vous connecter si vous perdez accès à votre application d\'authentification.'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """
    Désactive le 2FA pour l'utilisateur connecté
    
    Exigences: 25.2
    """
    from .serializers import Disable2FASerializer
    from .services import TwoFactorAuthService
    
    serializer = Disable2FASerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    password = serializer.validated_data['password']
    
    # Désactiver le 2FA
    result = TwoFactorAuthService.disable_2fa(user, password)
    
    if result['status'] == 'success':
        return Response({
            'message': result['message']
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': result['message']
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_2fa(request):
    """
    Vérifie le token 2FA lors de la connexion
    
    Utilisé après une connexion réussie pour les utilisateurs ayant le 2FA activé
    
    Exigences: 25.2
    """
    from .serializers import Verify2FASerializer
    from .services import TwoFactorAuthService
    
    serializer = Verify2FASerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    token = serializer.validated_data['token']
    
    try:
        user = User.objects.get(phone_number=phone_number)
        
        # Vérifier si le 2FA est activé
        if not user.two_factor_enabled:
            return Response({
                'error': 'Le 2FA n\'est pas activé pour ce compte'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le token TOTP ou le code de secours
        is_valid = False
        used_backup = False
        
        if len(token) == 6:
            # Token TOTP
            is_valid = TwoFactorAuthService.verify_token(user.two_factor_secret, token)
        elif len(token) == 8:
            # Code de secours
            is_valid = TwoFactorAuthService.verify_backup_code(user, token)
            used_backup = is_valid
        
        if not is_valid:
            return Response({
                'error': 'Token invalide'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Générer les tokens JWT
        tokens = JWTAuthService.generate_tokens(user)
        
        # Créer la session dans Redis
        from .session_service import SessionManagementService
        
        # Récupérer l'IP et le user agent depuis la requête
        # Note: Ces informations doivent être passées depuis le frontend ou extraites de la requête
        client_ip = request.META.get('REMOTE_ADDR', 'Unknown')
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0]
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        SessionManagementService.create_session(
            user_id=user.id,
            token=tokens['access_token'],
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        response_data = {
            'message': 'Authentification 2FA réussie',
            'user': UserSerializer(user).data,
            'tokens': tokens
        }
        
        if used_backup:
            response_data['warning'] = 'Vous avez utilisé un code de secours. Il ne peut plus être réutilisé.'
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_2fa_status(request):
    """
    Vérifie le statut du 2FA pour l'utilisateur connecté
    
    Exigences: 25.2
    """
    from .services import TwoFactorAuthService
    
    user = request.user
    status_info = TwoFactorAuthService.check_2fa_required(user)
    
    return Response({
        'user_type': user.user_type,
        'two_factor_required': status_info['required'],
        'two_factor_enabled': status_info['enabled'],
        'message': status_info['message']
    }, status=status.HTTP_200_OK)


# ============================================
# Endpoints de gestion des sessions
# Exigences: 40.1, 40.2, 40.3, 40.4, 40.5
# ============================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Déconnexion de l'utilisateur avec invalidation du token
    
    Invalide la session actuelle dans Redis
    
    Exigences: 40.2
    """
    from .session_service import SessionManagementService
    
    # Récupérer le token depuis l'en-tête Authorization
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({
            'error': 'Token non fourni'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    token = auth_header.split(' ')[1]
    
    # Invalider la session
    success = SessionManagementService.invalidate_session(request.user.id, token)
    
    if success:
        return Response({
            'message': 'Déconnexion réussie'
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'message': 'Session déjà invalide ou expirée'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_all_devices(request):
    """
    Déconnexion de tous les appareils
    
    Invalide toutes les sessions actives de l'utilisateur
    
    Exigences: 40.3
    """
    from .session_service import SessionManagementService
    
    # Invalider toutes les sessions
    count = SessionManagementService.invalidate_all_sessions(request.user.id)
    
    return Response({
        'message': f'Déconnexion réussie de {count} appareil(s)',
        'sessions_invalidated': count
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_sessions(request):
    """
    Récupère la liste des sessions actives de l'utilisateur
    
    Affiche les informations sur chaque session:
    - Type d'appareil (Desktop, Mobile, Tablet)
    - Navigateur
    - Système d'exploitation
    - Adresse IP
    - Localisation approximative
    - Date de création
    - Date de dernière activité
    
    Exigences: 40.4, 40.5
    """
    from .session_service import SessionManagementService
    
    sessions = SessionManagementService.get_active_sessions(request.user.id)
    
    return Response({
        'sessions': sessions,
        'total': len(sessions)
    }, status=status.HTTP_200_OK)


# ============================================
# Agronomist Registration
# ============================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_agronomist(request):
    """
    Inscription d'un agronome avec documents justificatifs
    
    Exigences: 7.1, 7.2, 7.3, 7.4
    
    Étapes:
    1. Valider les données de base (nom, téléphone, canton, spécialisations)
    2. Créer l'utilisateur avec type AGRONOME
    3. Créer le profil agronome avec statut EN_ATTENTE
    4. Gérer l'upload des documents justificatifs
    5. Envoyer le code de vérification SMS
    6. Retourner les informations
    """
    from .serializers import AgronomeRegistrationSerializer
    from .models import AgronomeProfile, DocumentJustificatif
    from apps.locations.models import Canton
    from django.db import transaction
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Vérifier le rate limiting par IP
    client_ip = get_client_ip(request)
    rate_limit = RateLimitService.check_rate_limit(client_ip, action='register')
    
    if rate_limit['is_blocked']:
        return Response({
            'error': 'Trop de tentatives. Veuillez réessayer plus tard.',
            'blocked_until': rate_limit.get('blocked_until')
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    # Préparer les données pour la validation
    data = request.data.copy()
    
    # Gérer les fichiers uploadés
    documents = request.FILES.getlist('documents')
    types_documents = request.data.getlist('types_documents')
    
    if documents:
        data['documents'] = documents
    if types_documents:
        data['types_documents'] = types_documents
    
    serializer = AgronomeRegistrationSerializer(data=data)
    
    if not serializer.is_valid():
        RateLimitService.record_attempt(client_ip, action='register', success=False)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        with transaction.atomic():
            # Créer l'utilisateur
            validated_data = serializer.validated_data
            
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                phone_number=validated_data['phone_number'],
                password=validated_data['password'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                user_type='AGRONOME'
            )
            
            # Créer le profil agronome avec statut EN_ATTENTE (Exigence 7.3)
            canton = Canton.objects.get(id=validated_data['canton_rattachement'])
            
            agronome_profile = AgronomeProfile.objects.create(
                user=user,
                canton_rattachement=canton,
                specialisations=validated_data['specialisations'],
                statut_validation='EN_ATTENTE'
            )
            
            # Gérer l'upload des documents justificatifs (Exigence 7.4)
            documents_uploaded = []
            if documents and types_documents:
                for document, type_doc in zip(documents, types_documents):
                    doc_justificatif = DocumentJustificatif.objects.create(
                        agronome_profile=agronome_profile,
                        type_document=type_doc,
                        fichier=document,
                        nom_fichier=document.name
                    )
                    documents_uploaded.append({
                        'id': doc_justificatif.id,
                        'type': doc_justificatif.get_type_document_display(),
                        'nom_fichier': doc_justificatif.nom_fichier
                    })
            
            # Envoyer le code de vérification SMS
            sms_result = SMSVerificationService.send_verification_code(user.phone_number)
            
            # Enregistrer la tentative réussie
            RateLimitService.record_attempt(client_ip, action='register', success=True)
            
            logger.info(
                f"Nouvel agronome inscrit: {user.username} - Canton: {canton.nom} - "
                f"Spécialisations: {', '.join(validated_data['specialisations'])}"
            )
            
            return Response({
                'message': 'Inscription réussie. Votre demande est en attente de validation. '
                          'Un code de vérification a été envoyé par SMS.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': user.user_type
                },
                'agronome_profile': {
                    'canton_rattachement': {
                        'id': canton.id,
                        'nom': canton.nom
                    },
                    'specialisations': validated_data['specialisations'],
                    'statut_validation': 'EN_ATTENTE',
                    'badge_valide': False
                },
                'documents_uploaded': documents_uploaded,
                'sms_sent': sms_result['status'] == 'success'
            }, status=status.HTTP_201_CREATED)
            
    except Canton.DoesNotExist:
        RateLimitService.record_attempt(client_ip, action='register', success=False)
        return Response({
            'error': 'Canton invalide'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        RateLimitService.record_attempt(client_ip, action='register', success=False)
        logger.error(f"Erreur lors de l'inscription d'un agronome: {str(e)}")
        return Response({
            'error': 'Erreur lors de l\'inscription',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_agronomist_document(request):
    """
    Upload d'un document justificatif supplémentaire pour un agronome
    
    Exigence: 7.4
    
    Permet à un agronome d'ajouter des documents après l'inscription initiale
    """
    from .models import AgronomeProfile, DocumentJustificatif
    from .serializers import DocumentJustificatifSerializer
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Vérifier que l'utilisateur est un agronome
    if request.user.user_type != 'AGRONOME':
        return Response({
            'error': 'Seuls les agronomes peuvent uploader des documents justificatifs'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        agronome_profile = request.user.agronome_profile
    except AgronomeProfile.DoesNotExist:
        return Response({
            'error': 'Profil agronome non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Vérifier que le fichier est fourni
    if 'fichier' not in request.FILES:
        return Response({
            'error': 'Aucun fichier fourni'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Préparer les données
    data = {
        'type_document': request.data.get('type_document'),
        'fichier': request.FILES['fichier'],
        'nom_fichier': request.FILES['fichier'].name
    }
    
    serializer = DocumentJustificatifSerializer(data=data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Créer le document
        document = DocumentJustificatif.objects.create(
            agronome_profile=agronome_profile,
            type_document=data['type_document'],
            fichier=data['fichier'],
            nom_fichier=data['nom_fichier']
        )
        
        logger.info(
            f"Document ajouté pour agronome {request.user.username}: "
            f"{document.get_type_document_display()}"
        )
        
        return Response({
            'message': 'Document uploadé avec succès',
            'document': {
                'id': document.id,
                'type': document.get_type_document_display(),
                'nom_fichier': document.nom_fichier,
                'uploaded_at': document.uploaded_at
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'upload d'un document: {str(e)}")
        return Response({
            'error': 'Erreur lors de l\'upload du document',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agronomist_documents(request):
    """
    Récupère la liste des documents justificatifs d'un agronome
    
    Exigence: 7.4
    """
    from .models import AgronomeProfile, DocumentJustificatif
    from .serializers import DocumentJustificatifSerializer
    
    # Vérifier que l'utilisateur est un agronome
    if request.user.user_type != 'AGRONOME':
        return Response({
            'error': 'Seuls les agronomes peuvent consulter leurs documents'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        agronome_profile = request.user.agronome_profile
        documents = DocumentJustificatif.objects.filter(agronome_profile=agronome_profile)
        
        serializer = DocumentJustificatifSerializer(documents, many=True)
        
        return Response({
            'documents': serializer.data,
            'count': documents.count()
        }, status=status.HTTP_200_OK)
        
    except AgronomeProfile.DoesNotExist:
        return Response({
            'error': 'Profil agronome non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_agronomist(request, agronomist_id):
    """
    Valider ou rejeter une demande d'agronome (admin uniquement)
    
    Exigences: 7.5, 7.6
    
    POST /api/v1/agronomists/{id}/validate
    
    Body:
    {
        "approved": true/false,
        "motif_rejet": "Raison du rejet" (requis si approved=false)
    }
    
    Workflow:
    1. Vérifier que l'utilisateur est admin
    2. Récupérer le profil agronome
    3. Valider ou rejeter selon le paramètre approved
    4. Si validé: Statut VALIDE + Badge Agronome_Validé (Exigence 7.5)
    5. Si rejeté: Statut REJETE + Notification avec motif (Exigence 7.6)
    """
    from .models import AgronomeProfile, User
    from .services import ValidationWorkflowService
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Vérifier que l'utilisateur est un administrateur
    if not request.user.is_staff and not request.user.is_superuser:
        return Response({
            'error': 'Accès refusé. Seuls les administrateurs peuvent valider les agronomes.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Récupérer les paramètres
    approved = request.data.get('approved')
    motif_rejet = request.data.get('motif_rejet', '').strip()
    
    # Validation des paramètres
    if approved is None:
        return Response({
            'error': 'Le paramètre "approved" est requis (true ou false)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not approved and not motif_rejet:
        return Response({
            'error': 'Un motif de rejet est requis lorsque approved=false'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Récupérer le profil agronome
    try:
        user = User.objects.get(id=agronomist_id, user_type='AGRONOME')
        agronome_profile = AgronomeProfile.objects.select_related(
            'user', 'canton_rattachement'
        ).get(user=user)
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur agronome non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    except AgronomeProfile.DoesNotExist:
        return Response({
            'error': 'Profil agronome non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Effectuer la validation via le service
    result = ValidationWorkflowService.validate_agronomist(
        agronome_profile=agronome_profile,
        admin_user=request.user,
        approved=approved,
        motif_rejet=motif_rejet if not approved else None
    )
    
    if not result['success']:
        return Response({
            'error': result['error']
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Retourner le résultat avec les détails complets
    response_data = {
        'message': result['message'],
        'agronome': result['agronome']
    }
    
    # Ajouter les informations complètes du profil
    response_data['agronome'].update({
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone_number': user.phone_number,
        'canton_rattachement': {
            'id': agronome_profile.canton_rattachement.id,
            'nom': agronome_profile.canton_rattachement.nom
        },
        'specialisations': agronome_profile.specialisations
    })
    
    logger.info(
        f"Validation effectuée par {request.user.username} pour l'agronome {user.username}: "
        f"{'Approuvé' if approved else 'Rejeté'}"
    )
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_agronomists(request):
    """
    Récupérer la liste des agronomes en attente de validation (admin uniquement)
    
    GET /api/v1/agronomists/pending
    
    Retourne la liste des profils agronomes avec statut EN_ATTENTE
    """
    from .services import ValidationWorkflowService
    
    # Vérifier que l'utilisateur est un administrateur
    if not request.user.is_staff and not request.user.is_superuser:
        return Response({
            'error': 'Accès refusé. Seuls les administrateurs peuvent consulter cette liste.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Récupérer les profils en attente
    result = ValidationWorkflowService.get_pending_validations()
    
    return Response({
        'count': result['count'],
        'profiles': result['profiles']
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_agronomist_details(request, agronomist_id):
    """
    Récupérer les détails complets d'un agronome incluant ses documents (admin uniquement)
    
    GET /api/v1/agronomists/{id}/details
    
    Retourne le profil complet avec documents justificatifs pour validation
    """
    from .models import AgronomeProfile, User
    
    # Vérifier que l'utilisateur est un administrateur
    if not request.user.is_staff and not request.user.is_superuser:
        return Response({
            'error': 'Accès refusé. Seuls les administrateurs peuvent consulter ces détails.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Récupérer le profil agronome avec documents
    try:
        user = User.objects.get(id=agronomist_id, user_type='AGRONOME')
        agronome_profile = AgronomeProfile.objects.select_related(
            'user', 'canton_rattachement', 'canton_rattachement__prefecture', 
            'canton_rattachement__prefecture__region'
        ).prefetch_related('documents_justificatifs').get(user=user)
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur agronome non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    except AgronomeProfile.DoesNotExist:
        return Response({
            'error': 'Profil agronome non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Construire la réponse avec tous les détails
    documents = []
    for doc in agronome_profile.documents_justificatifs.all():
        documents.append({
            'id': doc.id,
            'type': doc.get_type_document_display(),
            'type_code': doc.type_document,
            'nom_fichier': doc.nom_fichier,
            'url': doc.fichier.url if doc.fichier else None,
            'uploaded_at': doc.uploaded_at.isoformat()
        })
    
    response_data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone_number': user.phone_number,
        'date_joined': user.date_joined.isoformat(),
        'profile': {
            'canton_rattachement': {
                'id': agronome_profile.canton_rattachement.id,
                'nom': agronome_profile.canton_rattachement.nom,
                'prefecture': {
                    'id': agronome_profile.canton_rattachement.prefecture.id,
                    'nom': agronome_profile.canton_rattachement.prefecture.nom,
                    'region': {
                        'id': agronome_profile.canton_rattachement.prefecture.region.id,
                        'nom': agronome_profile.canton_rattachement.prefecture.region.nom
                    }
                }
            },
            'specialisations': agronome_profile.specialisations,
            'statut_validation': agronome_profile.statut_validation,
            'statut_validation_display': agronome_profile.get_statut_validation_display(),
            'badge_valide': agronome_profile.badge_valide,
            'date_validation': agronome_profile.date_validation.isoformat() if agronome_profile.date_validation else None,
            'motif_rejet': agronome_profile.motif_rejet,
            'note_moyenne': float(agronome_profile.note_moyenne),
            'nombre_avis': agronome_profile.nombre_avis
        },
        'documents': documents,
        'nombre_documents': len(documents)
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def agronomist_directory(request):
    """
    Annuaire public des agronomes validés avec filtres
    Exigences: 8.1, 8.2, 8.3, 8.4
    
    GET /api/v1/agronomists
    
    Query Parameters:
    - region: ID de la région (optionnel)
    - prefecture: ID de la préfecture (optionnel)
    - canton: ID du canton (optionnel)
    - specialisation: Spécialisation recherchée (optionnel)
    - page: Numéro de page (défaut: 1)
    - page_size: Nombre d'éléments par page (défaut: 20, max: 100)
    
    Retourne la liste des agronomes validés avec pagination
    """
    from django.core.cache import cache
    from django.core.paginator import Paginator, EmptyPage
    from .models import AgronomeProfile
    from .serializers import AgronomeDirectorySerializer
    
    # Récupérer les paramètres de filtrage
    region_id = request.query_params.get('region')
    prefecture_id = request.query_params.get('prefecture')
    canton_id = request.query_params.get('canton')
    specialisation = request.query_params.get('specialisation')
    
    # Paramètres de pagination
    try:
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
    except ValueError:
        return Response({
            'error': 'Paramètres de pagination invalides'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Construire la clé de cache
    cache_key = f"agronomist_directory:region_{region_id}:prefecture_{prefecture_id}:canton_{canton_id}:spec_{specialisation}:page_{page}:size_{page_size}"
    
    # Vérifier le cache Redis (Exigence: optimiser avec cache Redis)
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data, status=status.HTTP_200_OK)
    
    # Construire la requête de base - uniquement les profils validés (Exigence: 8.2)
    queryset = AgronomeProfile.objects.filter(
        statut_validation='VALIDE',
        badge_valide=True
    ).select_related(
        'user',
        'canton_rattachement',
        'canton_rattachement__prefecture',
        'canton_rattachement__prefecture__region'
    )
    
    # Appliquer les filtres (Exigence: 8.1)
    if canton_id:
        # Filtrer par canton (Exigence: 8.3)
        queryset = queryset.filter(canton_rattachement_id=canton_id)
    elif prefecture_id:
        # Filtrer par préfecture
        queryset = queryset.filter(canton_rattachement__prefecture_id=prefecture_id)
    elif region_id:
        # Filtrer par région
        queryset = queryset.filter(canton_rattachement__prefecture__region_id=region_id)
    
    # Filtrer par spécialisation (Exigence: 8.1)
    if specialisation:
        queryset = queryset.filter(specialisations__contains=[specialisation])
    
    # Trier par note moyenne décroissante, puis par nombre d'avis
    queryset = queryset.order_by('-note_moyenne', '-nombre_avis', 'user__first_name')
    
    # Pagination
    paginator = Paginator(queryset, page_size)
    
    try:
        agronomes_page = paginator.page(page)
    except EmptyPage:
        agronomes_page = paginator.page(paginator.num_pages) if paginator.num_pages > 0 else []
    
    # Sérialiser les données (Exigence: 8.4 - nom, spécialisations, Canton, note moyenne, nombre d'avis)
    serializer = AgronomeDirectorySerializer(agronomes_page, many=True)
    
    # Construire la réponse
    response_data = {
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': page,
        'page_size': page_size,
        'next': page < paginator.num_pages,
        'previous': page > 1,
        'results': serializer.data
    }
    
    # Mettre en cache pour 5 minutes
    cache.set(cache_key, response_data, timeout=300)
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def agronomist_public_detail(request, agronomist_id):
    """
    Page de détails publique d'un agronome validé
    Exigence: 8.5
    
    GET /api/v1/agronomists/{id}
    
    Affiche:
    - Le profil complet avec spécialisations
    - Les avis et notations (quand le système de notation sera implémenté)
    - Un bouton de contact pour les exploitants vérifiés
    
    Accessible à tous, mais le bouton de contact n'est visible que pour les exploitants vérifiés
    """
    from django.core.cache import cache
    from .models import AgronomeProfile, User, ExploitantProfile
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Construire la clé de cache
    cache_key = f"agronomist_public_detail:{agronomist_id}"
    
    # Essayer de récupérer depuis le cache (gérer les erreurs Redis gracieusement)
    cached_data = None
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            # Ajouter les informations de l'utilisateur connecté
            if request.user.is_authenticated:
                cached_data['can_contact'] = _can_contact_agronomist(request.user)
                cached_data['is_verified_farmer'] = _is_verified_farmer(request.user)
            else:
                cached_data['can_contact'] = False
                cached_data['is_verified_farmer'] = False
            
            return Response(cached_data, status=status.HTTP_200_OK)
    except Exception as e:
        # Si Redis n'est pas disponible, continuer sans cache
        logger.warning(f"Cache unavailable: {str(e)}")
    
    # Récupérer le profil agronome
    try:
        user = User.objects.get(id=agronomist_id, user_type='AGRONOME')
        agronome_profile = AgronomeProfile.objects.select_related(
            'user',
            'canton_rattachement',
            'canton_rattachement__prefecture',
            'canton_rattachement__prefecture__region'
        ).get(user=user)
    except User.DoesNotExist:
        return Response({
            'error': 'Agronome non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    except AgronomeProfile.DoesNotExist:
        return Response({
            'error': 'Profil agronome non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Vérifier que l'agronome est validé (seuls les profils validés sont publics)
    if agronome_profile.statut_validation != 'VALIDE' or not agronome_profile.badge_valide:
        return Response({
            'error': 'Ce profil n\'est pas accessible publiquement'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Construire les données du profil complet
    profile_data = {
        'id': user.id,
        'nom_complet': f"{user.first_name} {user.last_name}".strip() or user.username,
        'username': user.username,
        'photo_profil': user.photo_profil.url if user.photo_profil else None,
        'date_inscription': user.date_joined.isoformat(),
        
        # Informations de localisation
        'canton': {
            'id': agronome_profile.canton_rattachement.id,
            'nom': agronome_profile.canton_rattachement.nom
        },
        'prefecture': {
            'id': agronome_profile.canton_rattachement.prefecture.id,
            'nom': agronome_profile.canton_rattachement.prefecture.nom
        },
        'region': {
            'id': agronome_profile.canton_rattachement.prefecture.region.id,
            'nom': agronome_profile.canton_rattachement.prefecture.region.nom
        },
        
        # Spécialisations
        'specialisations': agronome_profile.specialisations,
        
        # Badge et statut
        'badge_valide': agronome_profile.badge_valide,
        'statut_validation': agronome_profile.statut_validation,
        
        # Notations et avis
        'note_moyenne': float(agronome_profile.note_moyenne),
        'nombre_avis': agronome_profile.nombre_avis,
        'avis': [],  # TODO: Sera rempli quand le système de notation sera implémenté (Phase V1, tâche 16)
        
        # Statistiques (à implémenter plus tard)
        'nombre_missions_completees': 0,  # TODO: Compter les missions terminées
        'taux_reussite': 100.0,  # TODO: Calculer le taux de réussite
    }
    
    # Essayer de mettre en cache (gérer les erreurs Redis gracieusement)
    try:
        cache.set(cache_key, profile_data, timeout=600)
    except Exception as e:
        # Si Redis n'est pas disponible, continuer sans cache
        logger.warning(f"Unable to cache data: {str(e)}")
    
    # Ajouter les informations spécifiques à l'utilisateur connecté
    if request.user.is_authenticated:
        profile_data['can_contact'] = _can_contact_agronomist(request.user)
        profile_data['is_verified_farmer'] = _is_verified_farmer(request.user)
    else:
        profile_data['can_contact'] = False
        profile_data['is_verified_farmer'] = False
    
    logger.info(f"Consultation du profil public de l'agronome {user.username}")
    
    return Response(profile_data, status=status.HTTP_200_OK)


def _is_verified_farmer(user):
    """
    Vérifie si l'utilisateur est un exploitant vérifié
    Exigence: 8.5 - Bouton de contact pour les exploitants vérifiés
    """
    if user.user_type != 'EXPLOITANT':
        return False
    
    try:
        exploitant_profile = user.exploitant_profile
        return exploitant_profile.statut_verification == 'VERIFIE'
    except:
        return False


def _can_contact_agronomist(user):
    """
    Détermine si l'utilisateur peut contacter l'agronome
    
    Règles:
    - Seuls les exploitants vérifiés peuvent contacter les agronomes
    - Les administrateurs peuvent aussi contacter
    """
    if user.is_staff or user.is_superuser:
        return True
    
    return _is_verified_farmer(user)



# ============================================
# FARM VERIFICATION ENDPOINTS
# ============================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def farm_verification_request(request):
    """
    Demande de vérification d'exploitation agricole
    
    Exigences: 10.1, 10.2, 10.3, 10.4
    
    Processus:
    1. Valider que l'utilisateur est un exploitant
    2. Valider la superficie minimale (10 hectares)
    3. Valider les coordonnées GPS
    4. Valider la cohérence GPS/superficie
    5. Uploader les documents justificatifs
    6. Créer ou mettre à jour le profil exploitant
    7. Changer le statut en EN_ATTENTE
    """
    from .serializers import FarmVerificationRequestSerializer
    from .models import ExploitantProfile, FarmVerificationDocument
    from apps.locations.models import Canton
    from .gps_validation import GPSValidationService
    from django.db import transaction
    
    # Vérifier que l'utilisateur est un exploitant
    if request.user.user_type != 'EXPLOITANT':
        return Response(
            {
                'error': 'Seuls les exploitants peuvent demander une vérification d\'exploitation',
                'code': 'NOT_EXPLOITANT'
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Valider les données
    serializer = FarmVerificationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                'error': 'Données invalides',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    validated_data = serializer.validated_data
    
    try:
        with transaction.atomic():
            # Récupérer ou créer le profil exploitant
            canton = Canton.objects.get(id=validated_data['canton_principal'])
            
            profile, created = ExploitantProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    'superficie_totale': validated_data['superficie_totale'],
                    'canton_principal': canton,
                    'coordonnees_gps': validated_data['coordonnees_gps'],
                    'cultures_actuelles': validated_data.get('cultures_actuelles', []),
                    'statut_verification': 'EN_ATTENTE'
                }
            )
            
            if not created:
                # Mettre à jour le profil existant
                profile.superficie_totale = validated_data['superficie_totale']
                profile.canton_principal = canton
                profile.coordonnees_gps = validated_data['coordonnees_gps']
                profile.cultures_actuelles = validated_data.get('cultures_actuelles', [])
                profile.statut_verification = 'EN_ATTENTE'
                profile.motif_rejet = None  # Réinitialiser le motif de rejet
                profile.save()
            
            # Supprimer les anciens documents de vérification
            FarmVerificationDocument.objects.filter(exploitant_profile=profile).delete()
            
            # Uploader les nouveaux documents
            documents = validated_data['documents']
            types_documents = validated_data['types_documents']
            
            uploaded_documents = []
            for document, type_document in zip(documents, types_documents):
                doc = FarmVerificationDocument.objects.create(
                    exploitant_profile=profile,
                    type_document=type_document,
                    fichier=document,
                    nom_fichier=document.name
                )
                uploaded_documents.append(doc)
            
            # Récupérer les détails de validation GPS
            validation_details = validated_data.get('_validation_details', {})
            
            return Response(
                {
                    'message': 'Demande de vérification soumise avec succès',
                    'profile': {
                        'superficie_totale': str(profile.superficie_totale),
                        'canton_principal': {
                            'id': profile.canton_principal.id,
                            'nom': profile.canton_principal.nom
                        },
                        'statut_verification': profile.statut_verification,
                        'cultures_actuelles': profile.cultures_actuelles,
                        'documents_uploaded': len(uploaded_documents)
                    },
                    'validation_gps': validation_details
                },
                status=status.HTTP_201_CREATED
            )
    
    except Canton.DoesNotExist:
        return Response(
            {
                'error': 'Canton invalide',
                'code': 'INVALID_CANTON'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {
                'error': 'Erreur lors de la soumission de la demande',
                'details': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def farm_verification_status(request):
    """
    Récupère le statut de vérification de l'exploitation de l'utilisateur connecté
    
    Exigences: 10.4, 10.5
    """
    from .serializers import FarmVerificationStatusSerializer
    from .models import ExploitantProfile
    
    # Vérifier que l'utilisateur est un exploitant
    if request.user.user_type != 'EXPLOITANT':
        return Response(
            {
                'error': 'Seuls les exploitants peuvent consulter le statut de vérification',
                'code': 'NOT_EXPLOITANT'
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        profile = ExploitantProfile.objects.select_related(
            'canton_principal',
            'canton_principal__prefecture',
            'canton_principal__prefecture__region'
        ).prefetch_related('documents_verification').get(user=request.user)
        
        serializer = FarmVerificationStatusSerializer(profile)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except ExploitantProfile.DoesNotExist:
        return Response(
            {
                'error': 'Profil exploitant non trouvé',
                'code': 'PROFILE_NOT_FOUND',
                'message': 'Vous devez d\'abord soumettre une demande de vérification'
            },
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def farm_premium_features(request):
    """
    Récupère les fonctionnalités premium disponibles pour l'exploitant vérifié
    
    Exigences: 10.5, 10.6
    """
    from .models import ExploitantProfile
    
    # Vérifier que l'utilisateur est un exploitant
    if request.user.user_type != 'EXPLOITANT':
        return Response(
            {
                'error': 'Seuls les exploitants peuvent accéder aux fonctionnalités premium',
                'code': 'NOT_EXPLOITANT'
            },
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        profile = ExploitantProfile.objects.get(user=request.user)
        
        is_verified = profile.statut_verification == 'VERIFIE'
        
        premium_features = {
            'is_verified': is_verified,
            'statut_verification': profile.statut_verification,
            'features': {
                'dashboard_avance': {
                    'enabled': is_verified,
                    'description': 'Tableau de bord avec statistiques détaillées'
                },
                'recrutement_agronomes': {
                    'enabled': is_verified,
                    'description': 'Recrutement d\'agronomes validés'
                },
                'recrutement_ouvriers': {
                    'enabled': is_verified,
                    'description': 'Recrutement d\'ouvriers saisonniers'
                },
                'prevente_agricole': {
                    'enabled': is_verified,
                    'description': 'Création de préventes agricoles'
                },
                'analyses_marche': {
                    'enabled': is_verified,
                    'description': 'Accès aux analyses de marché et prévisions de prix'
                },
                'optimisation_logistique': {
                    'enabled': is_verified,
                    'description': 'Optimisation des itinéraires et coûts de transport'
                },
                'recommandations_cultures': {
                    'enabled': is_verified,
                    'description': 'Recommandations de cultures adaptées'
                },
                'irrigation_intelligente': {
                    'enabled': is_verified,
                    'description': 'Estimation des besoins en eau et zones irrigables'
                }
            }
        }
        
        if not is_verified:
            premium_features['message'] = 'Votre exploitation doit être vérifiée pour accéder aux fonctionnalités premium'
            if profile.statut_verification == 'EN_ATTENTE':
                premium_features['message'] = 'Votre demande de vérification est en cours de traitement'
            elif profile.statut_verification == 'REJETE':
                premium_features['message'] = f'Votre demande de vérification a été rejetée. Motif: {profile.motif_rejet}'
        
        return Response(premium_features, status=status.HTTP_200_OK)
    
    except ExploitantProfile.DoesNotExist:
        return Response(
            {
                'error': 'Profil exploitant non trouvé',
                'code': 'PROFILE_NOT_FOUND',
                'is_verified': False,
                'message': 'Vous devez d\'abord soumettre une demande de vérification d\'exploitation'
            },
            status=status.HTTP_404_NOT_FOUND
        )



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_farm(request, farm_id):
    """
    Valider ou rejeter une demande de vérification d'exploitation (admin uniquement)
    
    Exigences: 10.4, 10.5, 10.6
    
    POST /api/v1/farms/{id}/verify
    
    Body:
    {
        "approved": true/false,
        "motif_rejet": "Raison du rejet" (requis si approved=false)
    }
    
    Workflow:
    1. Vérifier que l'utilisateur est admin
    2. Récupérer le profil exploitant
    3. Valider ou rejeter selon le paramètre approved
    4. Si validé: Statut VERIFIE + Déblocage fonctionnalités premium (Exigence 10.5)
    5. Si rejeté: Statut REJETE + Notification avec motif (Exigence 10.6)
    """
    from .models import ExploitantProfile, User
    from .services import FarmVerificationService
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Vérifier que l'utilisateur est un administrateur
    if not request.user.is_staff and not request.user.is_superuser:
        return Response({
            'error': 'Accès refusé. Seuls les administrateurs peuvent vérifier les exploitations.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Récupérer les paramètres
    approved = request.data.get('approved')
    motif_rejet = request.data.get('motif_rejet', '').strip()
    
    # Validation des paramètres
    if approved is None:
        return Response({
            'error': 'Le paramètre "approved" est requis (true ou false)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not approved and not motif_rejet:
        return Response({
            'error': 'Un motif de rejet est requis lorsque approved=false'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Récupérer le profil exploitant
    try:
        user = User.objects.get(id=farm_id, user_type='EXPLOITANT')
        exploitant_profile = ExploitantProfile.objects.select_related(
            'user', 'canton_principal', 'canton_principal__prefecture',
            'canton_principal__prefecture__region'
        ).prefetch_related('documents_verification').get(user=user)
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur exploitant non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    except ExploitantProfile.DoesNotExist:
        return Response({
            'error': 'Profil exploitant non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Effectuer la vérification via le service
    result = FarmVerificationService.verify_farm(
        exploitant_profile=exploitant_profile,
        admin_user=request.user,
        approved=approved,
        motif_rejet=motif_rejet if not approved else None
    )
    
    if not result['success']:
        return Response({
            'error': result['error']
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Retourner le résultat avec les détails complets
    response_data = {
        'message': result['message'],
        'exploitant': result['exploitant']
    }
    
    # Ajouter les informations complètes du profil
    response_data['exploitant'].update({
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone_number': user.phone_number,
        'canton_principal': {
            'id': exploitant_profile.canton_principal.id,
            'nom': exploitant_profile.canton_principal.nom,
            'prefecture': {
                'id': exploitant_profile.canton_principal.prefecture.id,
                'nom': exploitant_profile.canton_principal.prefecture.nom,
                'region': {
                    'id': exploitant_profile.canton_principal.prefecture.region.id,
                    'nom': exploitant_profile.canton_principal.prefecture.region.nom
                }
            }
        },
        'cultures_actuelles': exploitant_profile.cultures_actuelles,
        'coordonnees_gps': exploitant_profile.coordonnees_gps
    })
    
    logger.info(
        f"Vérification effectuée par {request.user.username} pour l'exploitant {user.username}: "
        f"{'Approuvé' if approved else 'Rejeté'}"
    )
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_farms(request):
    """
    Récupérer la liste des exploitations en attente de vérification (admin uniquement)
    
    GET /api/v1/farms/pending
    
    Retourne la liste des profils exploitants avec statut EN_ATTENTE
    """
    from .services import FarmVerificationService
    
    # Vérifier que l'utilisateur est un administrateur
    if not request.user.is_staff and not request.user.is_superuser:
        return Response({
            'error': 'Accès refusé. Seuls les administrateurs peuvent consulter cette liste.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Récupérer les profils en attente
    result = FarmVerificationService.get_pending_verifications()
    
    return Response({
        'count': result['count'],
        'profiles': result['profiles']
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_farm_details(request, farm_id):
    """
    Récupérer les détails complets d'une exploitation incluant ses documents (admin uniquement)
    
    GET /api/v1/farms/{id}/details
    
    Retourne le profil complet avec documents justificatifs pour vérification
    """
    from .models import ExploitantProfile, User
    
    # Vérifier que l'utilisateur est un administrateur
    if not request.user.is_staff and not request.user.is_superuser:
        return Response({
            'error': 'Accès refusé. Seuls les administrateurs peuvent consulter ces détails.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Récupérer le profil exploitant avec documents
    try:
        user = User.objects.get(id=farm_id, user_type='EXPLOITANT')
        exploitant_profile = ExploitantProfile.objects.select_related(
            'user', 'canton_principal', 'canton_principal__prefecture', 
            'canton_principal__prefecture__region'
        ).prefetch_related('documents_verification').get(user=user)
    except User.DoesNotExist:
        return Response({
            'error': 'Utilisateur exploitant non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    except ExploitantProfile.DoesNotExist:
        return Response({
            'error': 'Profil exploitant non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Construire la réponse avec tous les détails
    documents = []
    for doc in exploitant_profile.documents_verification.all():
        documents.append({
            'id': doc.id,
            'type': doc.get_type_document_display(),
            'type_code': doc.type_document,
            'nom_fichier': doc.nom_fichier,
            'url': doc.fichier.url if doc.fichier else None,
            'uploaded_at': doc.uploaded_at.isoformat()
        })
    
    response_data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone_number': user.phone_number,
        'date_joined': user.date_joined.isoformat(),
        'profile': {
            'superficie_totale': str(exploitant_profile.superficie_totale),
            'canton_principal': {
                'id': exploitant_profile.canton_principal.id,
                'nom': exploitant_profile.canton_principal.nom,
                'prefecture': {
                    'id': exploitant_profile.canton_principal.prefecture.id,
                    'nom': exploitant_profile.canton_principal.prefecture.nom,
                    'region': {
                        'id': exploitant_profile.canton_principal.prefecture.region.id,
                        'nom': exploitant_profile.canton_principal.prefecture.region.nom
                    }
                }
            },
            'coordonnees_gps': exploitant_profile.coordonnees_gps,
            'cultures_actuelles': exploitant_profile.cultures_actuelles,
            'statut_verification': exploitant_profile.statut_verification,
            'statut_verification_display': exploitant_profile.get_statut_verification_display(),
            'date_verification': exploitant_profile.date_verification.isoformat() if exploitant_profile.date_verification else None,
            'motif_rejet': exploitant_profile.motif_rejet
        },
        'documents': documents,
        'nombre_documents': len(documents)
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def neon_exchange(request):
    """
    Échange un token Neon Auth (Better Auth) contre des tokens Django JWT.
    Crée ou synchronise l'utilisateur Django si nécessaire.
    """
    import uuid
    from .neon_auth import verify_neon_session

    token = request.data.get('token', '').strip()
    user_type = request.data.get('user_type', '').strip()

    if not token:
        return Response({'detail': 'Token requis.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        neon_user = verify_neon_session(token)
    except ValueError as e:
        return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    email = neon_user['email']
    neon_name = neon_user.get('name', '')
    name_parts = neon_name.split(' ', 1) if neon_name else ['', '']
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': email.split('@')[0][:20] + '_' + str(uuid.uuid4())[:6],
            'user_type': user_type,
            'phone_verified': True,
            'first_name': first_name,
            'last_name': last_name,
        }
    )

    if created:
        if user_type:
            user.user_type = user_type
        user.set_unusable_password()
        user.save()

    tokens = JWTAuthService.generate_tokens(user)

    return Response({
        'tokens': {
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
        },
        'user': UserSerializer(user).data,
        'created': created,
    }, status=status.HTTP_200_OK)
