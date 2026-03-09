"""
Documentation API pour les endpoints d'authentification
Utilise drf-spectacular pour générer la documentation Swagger/OpenAPI
"""

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes


# ============================================
# DOCUMENTATION: Authentification par Email
# ============================================

register_email_schema = extend_schema(
    summary="Inscription par email",
    description="""
    Crée un nouveau compte utilisateur avec email et mot de passe.
    
    **Règles de validation**:
    - Email valide et unique
    - Mot de passe minimum 8 caractères
    - Mot de passe doit contenir: majuscule, minuscule, chiffre, caractère spécial
    - Les deux mots de passe doivent correspondre
    
    **Types d'utilisateurs**:
    - `EXPLOITANT`: Agriculteur/Exploitant agricole
    - `AGRONOME`: Agronome professionnel
    - `OUVRIER`: Ouvrier agricole
    - `ACHETEUR`: Acheteur de produits agricoles
    - `FOURNISSEUR`: Fournisseur d'intrants
    """,
    request={
        'application/json': {
            'example': {
                'email': 'user@example.com',
                'password': 'SecurePass123!',
                'password_confirm': 'SecurePass123!',
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'user_type': 'EXPLOITANT'
            }
        }
    },
    responses={
        201: OpenApiResponse(
            description='Inscription réussie',
            response={
                'application/json': {
                    'example': {
                        'tokens': {
                            'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                            'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                        },
                        'user': {
                            'id': 1,
                            'email': 'user@example.com',
                            'first_name': 'Jean',
                            'last_name': 'Dupont',
                            'user_type': 'EXPLOITANT',
                            'is_active': True
                        }
                    }
                }
            }
        ),
        400: OpenApiResponse(description='Données invalides (email déjà utilisé, mot de passe faible, etc.)'),
        429: OpenApiResponse(description='Trop de tentatives d\'inscription')
    },
    tags=['Authentification']
)


login_email_schema = extend_schema(
    summary="Connexion par email",
    description="""
    Authentifie un utilisateur avec email et mot de passe.
    Retourne les tokens JWT (access + refresh) pour les requêtes suivantes.
    
    **Rate limiting**: 5 tentatives par minute par IP
    
    **Tokens JWT**:
    - `access_token`: Valide 1 heure, à inclure dans le header `Authorization: Bearer <token>`
    - `refresh_token`: Valide 24 heures, pour renouveler l'access token
    """,
    request={
        'application/json': {
            'example': {
                'email': 'user@example.com',
                'password': 'SecurePass123!'
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description='Connexion réussie',
            response={
                'application/json': {
                    'example': {
                        'tokens': {
                            'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                            'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                        },
                        'user': {
                            'id': 1,
                            'email': 'user@example.com',
                            'first_name': 'Jean',
                            'last_name': 'Dupont',
                            'user_type': 'EXPLOITANT'
                        }
                    }
                }
            }
        ),
        401: OpenApiResponse(description='Email ou mot de passe incorrect'),
        403: OpenApiResponse(description='Compte désactivé'),
        429: OpenApiResponse(description='Trop de tentatives de connexion')
    },
    tags=['Authentification']
)


login_with_cookies_schema = extend_schema(
    summary="Connexion sécurisée avec cookies HttpOnly",
    description="""
    Authentifie un utilisateur et stocke les tokens JWT dans des cookies HttpOnly.
    **Plus sécurisé** que la méthode classique car protège contre les attaques XSS.
    
    **Cookies configurés**:
    - `access_token`: HttpOnly, Secure (HTTPS), SameSite=Lax, durée 1h
    - `refresh_token`: HttpOnly, Secure (HTTPS), SameSite=Lax, durée 24h
    
    **Utilisation**:
    Les cookies sont automatiquement envoyés avec chaque requête.
    Pas besoin de gérer manuellement les tokens côté client.
    """,
    request={
        'application/json': {
            'example': {
                'email': 'user@example.com',
                'password': 'SecurePass123!'
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description='Connexion réussie, cookies définis',
            response={
                'application/json': {
                    'example': {
                        'user': {
                            'id': 1,
                            'email': 'user@example.com',
                            'first_name': 'Jean',
                            'last_name': 'Dupont'
                        },
                        'message': 'Connexion réussie'
                    }
                }
            }
        ),
        401: OpenApiResponse(description='Email ou mot de passe incorrect'),
        429: OpenApiResponse(description='Trop de tentatives')
    },
    tags=['Authentification']
)


refresh_token_schema = extend_schema(
    summary="Rafraîchir le token d'accès",
    description="""
    Génère un nouveau token d'accès à partir du refresh token.
    À utiliser quand l'access token expire (après 1 heure).
    
    **Header requis**: `Authorization: Bearer <refresh_token>`
    """,
    request={
        'application/json': {
            'example': {
                'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description='Token rafraîchi',
            response={
                'application/json': {
                    'example': {
                        'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                    }
                }
            }
        ),
        401: OpenApiResponse(description='Refresh token invalide ou expiré')
    },
    tags=['Authentification']
)


refresh_token_with_cookies_schema = extend_schema(
    summary="Rafraîchir le token (version cookies)",
    description="""
    Rafraîchit le token d'accès depuis le cookie refresh_token.
    Le nouveau access token est automatiquement stocké dans un cookie.
    
    **Cookies requis**: `refresh_token` (envoyé automatiquement)
    """,
    responses={
        200: OpenApiResponse(
            description='Token rafraîchi, cookie mis à jour',
            response={
                'application/json': {
                    'example': {
                        'message': 'Token rafraîchi'
                    }
                }
            }
        ),
        401: OpenApiResponse(description='Token invalide ou expiré')
    },
    tags=['Authentification']
)


logout_schema = extend_schema(
    summary="Déconnexion",
    description="""
    Déconnecte l'utilisateur en invalidant la session active.
    Le token JWT reste valide jusqu'à expiration mais la session est marquée comme inactive.
    
    **Header requis**: `Authorization: Bearer <access_token>`
    """,
    responses={
        200: OpenApiResponse(
            description='Déconnexion réussie',
            response={
                'application/json': {
                    'example': {
                        'message': 'Déconnexion réussie'
                    }
                }
            }
        ),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Authentification']
)


logout_with_cookies_schema = extend_schema(
    summary="Déconnexion (version cookies)",
    description="""
    Déconnecte l'utilisateur et supprime les cookies JWT.
    
    **Cookies supprimés**: `access_token`, `refresh_token`
    """,
    responses={
        200: OpenApiResponse(
            description='Déconnexion réussie, cookies supprimés',
            response={
                'application/json': {
                    'example': {
                        'message': 'Déconnexion réussie'
                    }
                }
            }
        ),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Authentification']
)


logout_all_devices_schema = extend_schema(
    summary="Déconnexion de tous les appareils",
    description="""
    Invalide toutes les sessions actives de l'utilisateur sur tous les appareils.
    Utile en cas de compromission de compte.
    
    **Header requis**: `Authorization: Bearer <access_token>`
    """,
    responses={
        200: OpenApiResponse(
            description='Toutes les sessions invalidées',
            response={
                'application/json': {
                    'example': {
                        'message': 'Déconnexion de tous les appareils réussie',
                        'sessions_invalidated': 3
                    }
                }
            }
        ),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Authentification']
)


# ============================================
# DOCUMENTATION: Gestion du Profil
# ============================================

get_profile_schema = extend_schema(
    summary="Obtenir le profil utilisateur",
    description="""
    Retourne les informations du profil de l'utilisateur connecté.
    
    **Header requis**: `Authorization: Bearer <access_token>`
    """,
    responses={
        200: OpenApiResponse(
            description='Profil utilisateur',
            response={
                'application/json': {
                    'example': {
                        'id': 1,
                        'email': 'user@example.com',
                        'first_name': 'Jean',
                        'last_name': 'Dupont',
                        'phone': '+22890123456',
                        'user_type': 'EXPLOITANT',
                        'is_active': True,
                        'is_verified': True,
                        'created_at': '2024-01-15T10:30:00Z'
                    }
                }
            }
        ),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Utilisateurs']
)


update_profile_schema = extend_schema(
    summary="Mettre à jour le profil",
    description="""
    Met à jour les informations du profil utilisateur.
    
    **Champs modifiables**:
    - first_name, last_name
    - phone
    - address, city, region
    - profile_picture (upload)
    
    **Header requis**: `Authorization: Bearer <access_token>`
    """,
    request={
        'multipart/form-data': {
            'example': {
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'phone': '+22890123456',
                'profile_picture': '<binary>'
            }
        }
    },
    responses={
        200: OpenApiResponse(description='Profil mis à jour'),
        400: OpenApiResponse(description='Données invalides'),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Utilisateurs']
)


change_password_schema = extend_schema(
    summary="Changer le mot de passe",
    description="""
    Change le mot de passe de l'utilisateur connecté.
    Nécessite l'ancien mot de passe pour validation.
    
    **Header requis**: `Authorization: Bearer <access_token>`
    """,
    request={
        'application/json': {
            'example': {
                'old_password': 'OldPass123!',
                'new_password': 'NewSecurePass456!',
                'new_password_confirm': 'NewSecurePass456!'
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description='Mot de passe changé',
            response={
                'application/json': {
                    'example': {
                        'message': 'Mot de passe changé avec succès'
                    }
                }
            }
        ),
        400: OpenApiResponse(description='Ancien mot de passe incorrect ou nouveau mot de passe invalide'),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Utilisateurs']
)


# ============================================
# DOCUMENTATION: Authentification 2FA
# ============================================

setup_2fa_schema = extend_schema(
    summary="Configurer l'authentification à deux facteurs (2FA)",
    description="""
    Génère un secret TOTP et un QR code pour configurer 2FA.
    L'utilisateur doit scanner le QR code avec une app comme Google Authenticator.
    
    **Header requis**: `Authorization: Bearer <access_token>`
    """,
    responses={
        200: OpenApiResponse(
            description='Secret 2FA généré',
            response={
                'application/json': {
                    'example': {
                        'secret': 'JBSWY3DPEHPK3PXP',
                        'qr_code': 'data:image/png;base64,iVBORw0KGgoAAAANS...',
                        'backup_codes': ['12345678', '87654321', '11223344']
                    }
                }
            }
        ),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Authentification']
)


enable_2fa_schema = extend_schema(
    summary="Activer 2FA",
    description="""
    Active l'authentification à deux facteurs après vérification du code TOTP.
    
    **Header requis**: `Authorization: Bearer <access_token>`
    """,
    request={
        'application/json': {
            'example': {
                'totp_code': '123456'
            }
        }
    },
    responses={
        200: OpenApiResponse(description='2FA activé'),
        400: OpenApiResponse(description='Code TOTP invalide'),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Authentification']
)


disable_2fa_schema = extend_schema(
    summary="Désactiver 2FA",
    description="""
    Désactive l'authentification à deux facteurs.
    Nécessite le mot de passe pour confirmation.
    
    **Header requis**: `Authorization: Bearer <access_token>`
    """,
    request={
        'application/json': {
            'example': {
                'password': 'SecurePass123!'
            }
        }
    },
    responses={
        200: OpenApiResponse(description='2FA désactivé'),
        400: OpenApiResponse(description='Mot de passe incorrect'),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Authentification']
)


verify_2fa_schema = extend_schema(
    summary="Vérifier le code 2FA lors de la connexion",
    description="""
    Vérifie le code TOTP lors de la connexion d'un utilisateur avec 2FA activé.
    À utiliser après une connexion réussie si l'utilisateur a 2FA activé.
    """,
    request={
        'application/json': {
            'example': {
                'email': 'user@example.com',
                'totp_code': '123456'
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description='Code 2FA valide, tokens retournés',
            response={
                'application/json': {
                    'example': {
                        'tokens': {
                            'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                            'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                        }
                    }
                }
            }
        ),
        400: OpenApiResponse(description='Code TOTP invalide'),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Authentification']
)


# ============================================
# DOCUMENTATION: Gestion des Sessions
# ============================================

active_sessions_schema = extend_schema(
    summary="Lister les sessions actives",
    description="""
    Retourne la liste de toutes les sessions actives de l'utilisateur.
    
    **Informations par session**:
    - Type d'appareil (Desktop, Mobile, Tablet)
    - Navigateur et version
    - Système d'exploitation
    - Adresse IP
    - Localisation approximative
    - Date de création
    - Date de dernière activité
    
    **Header requis**: `Authorization: Bearer <access_token>`
    """,
    responses={
        200: OpenApiResponse(
            description='Liste des sessions actives',
            response={
                'application/json': {
                    'example': {
                        'sessions': [
                            {
                                'id': 'session_123',
                                'device_type': 'Desktop',
                                'browser': 'Chrome 120',
                                'os': 'Windows 11',
                                'ip_address': '192.168.1.1',
                                'location': 'Lomé, Togo',
                                'created_at': '2024-01-15T10:30:00Z',
                                'last_activity': '2024-01-15T14:20:00Z',
                                'is_current': True
                            }
                        ],
                        'total': 1
                    }
                }
            }
        ),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Sessions']
)


check_2fa_status_schema = extend_schema(
    summary="Vérifier le statut 2FA",
    description="""
    Vérifie si le 2FA est requis et activé pour l'utilisateur connecté.
    
    **Header requis**: `Authorization: Bearer <access_token>`
    """,
    responses={
        200: OpenApiResponse(
            description='Statut 2FA',
            response={
                'application/json': {
                    'example': {
                        'user_type': 'AGRONOME',
                        'two_factor_required': True,
                        'two_factor_enabled': True,
                        'message': 'Le 2FA est activé'
                    }
                }
            }
        ),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Authentification']
)


# ============================================
# DOCUMENTATION: Inscription Agronomes
# ============================================

register_agronomist_schema = extend_schema(
    summary="Inscription d'un agronome",
    description="""
    Crée un compte agronome avec documents justificatifs.
    Le compte est créé avec statut EN_ATTENTE et nécessite validation admin.
    
    **Documents requis**:
    - Diplôme ou certificat
    - Pièce d'identité
    - Photo de profil (optionnel)
    
    **Spécialisations disponibles**:
    - Cultures vivrières
    - Cultures de rente
    - Élevage
    - Agroforesterie
    - Agriculture biologique
    - Irrigation
    """,
    request={
        'multipart/form-data': {
            'example': {
                'username': 'agronome_jean',
                'email': 'jean@example.com',
                'phone_number': '+22890123456',
                'password': 'SecurePass123!',
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'canton_rattachement': 1,
                'specialisations': ['Cultures vivrières', 'Irrigation'],
                'documents': '<binary>',
                'types_documents': ['DIPLOME', 'PIECE_IDENTITE']
            }
        }
    },
    responses={
        201: OpenApiResponse(
            description='Inscription réussie, en attente de validation',
            response={
                'application/json': {
                    'example': {
                        'message': 'Inscription réussie. Votre demande est en attente de validation.',
                        'user': {
                            'id': 1,
                            'username': 'agronome_jean',
                            'email': 'jean@example.com',
                            'user_type': 'AGRONOME'
                        },
                        'agronome_profile': {
                            'statut_validation': 'EN_ATTENTE',
                            'badge_valide': False
                        }
                    }
                }
            }
        ),
        400: OpenApiResponse(description='Données invalides'),
        429: OpenApiResponse(description='Trop de tentatives')
    },
    tags=['Agronomes']
)


validate_agronomist_schema = extend_schema(
    summary="Valider ou rejeter un agronome (Admin)",
    description="""
    Valide ou rejette une demande d'inscription d'agronome.
    
    **Accès**: Administrateurs uniquement
    
    **Si approuvé**:
    - Statut passe à VALIDE
    - Badge "Agronome_Validé" attribué
    - Notification envoyée à l'agronome
    
    **Si rejeté**:
    - Statut passe à REJETE
    - Notification avec motif envoyée
    """,
    request={
        'application/json': {
            'example': {
                'approved': True,
                'motif_rejet': 'Documents incomplets'
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description='Validation effectuée',
            response={
                'application/json': {
                    'example': {
                        'message': 'Agronome validé avec succès',
                        'agronome': {
                            'id': 1,
                            'statut_validation': 'VALIDE',
                            'badge_valide': True
                        }
                    }
                }
            }
        ),
        400: OpenApiResponse(description='Paramètres invalides'),
        403: OpenApiResponse(description='Accès refusé (non admin)'),
        404: OpenApiResponse(description='Agronome non trouvé')
    },
    tags=['Agronomes']
)


get_pending_agronomists_schema = extend_schema(
    summary="Liste des agronomes en attente (Admin)",
    description="""
    Retourne la liste des agronomes avec statut EN_ATTENTE.
    
    **Accès**: Administrateurs uniquement
    """,
    responses={
        200: OpenApiResponse(
            description='Liste des agronomes en attente',
            response={
                'application/json': {
                    'example': {
                        'count': 5,
                        'profiles': [
                            {
                                'id': 1,
                                'username': 'agronome_jean',
                                'first_name': 'Jean',
                                'last_name': 'Dupont',
                                'statut_validation': 'EN_ATTENTE',
                                'date_inscription': '2024-01-15T10:30:00Z'
                            }
                        ]
                    }
                }
            }
        ),
        403: OpenApiResponse(description='Accès refusé (non admin)')
    },
    tags=['Agronomes']
)


get_agronomist_details_schema = extend_schema(
    summary="Détails complets d'un agronome (Admin)",
    description="""
    Retourne les détails complets d'un agronome incluant documents justificatifs.
    
    **Accès**: Administrateurs uniquement
    """,
    responses={
        200: OpenApiResponse(
            description='Détails de l\'agronome',
            response={
                'application/json': {
                    'example': {
                        'id': 1,
                        'username': 'agronome_jean',
                        'first_name': 'Jean',
                        'last_name': 'Dupont',
                        'email': 'jean@example.com',
                        'profile': {
                            'canton_rattachement': {
                                'id': 1,
                                'nom': 'Golfe 1'
                            },
                            'specialisations': ['Cultures vivrières'],
                            'statut_validation': 'EN_ATTENTE'
                        },
                        'documents': [
                            {
                                'id': 1,
                                'type': 'Diplôme',
                                'nom_fichier': 'diplome.pdf',
                                'url': '/media/documents/diplome.pdf'
                            }
                        ]
                    }
                }
            }
        ),
        403: OpenApiResponse(description='Accès refusé (non admin)'),
        404: OpenApiResponse(description='Agronome non trouvé')
    },
    tags=['Agronomes']
)


agronomist_directory_schema = extend_schema(
    summary="Annuaire des agronomes validés",
    description="""
    Retourne la liste des agronomes validés avec filtres.
    
    **Filtres disponibles**:
    - `canton`: ID du canton
    - `specialisation`: Spécialisation recherchée
    - `search`: Recherche par nom
    
    **Accès**: Utilisateurs authentifiés uniquement
    """,
    parameters=[
        OpenApiParameter(name='canton', type=OpenApiTypes.INT, description='Filtrer par canton'),
        OpenApiParameter(name='specialisation', type=OpenApiTypes.STR, description='Filtrer par spécialisation'),
        OpenApiParameter(name='search', type=OpenApiTypes.STR, description='Rechercher par nom'),
    ],
    responses={
        200: OpenApiResponse(
            description='Liste des agronomes',
            response={
                'application/json': {
                    'example': {
                        'count': 10,
                        'results': [
                            {
                                'id': 1,
                                'first_name': 'Jean',
                                'last_name': 'Dupont',
                                'canton': 'Golfe 1',
                                'specialisations': ['Cultures vivrières'],
                                'rating': 4.5,
                                'missions_completed': 15
                            }
                        ]
                    }
                }
            }
        ),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Agronomes']
)


agronomist_public_detail_schema = extend_schema(
    summary="Profil public d'un agronome",
    description="""
    Retourne le profil public d'un agronome validé.
    
    **Informations publiques**:
    - Nom, canton, spécialisations
    - Note moyenne et nombre de missions
    - Disponibilité
    - Tarifs (si publics)
    
    **Accès**: Utilisateurs authentifiés uniquement
    """,
    responses={
        200: OpenApiResponse(
            description='Profil public de l\'agronome',
            response={
                'application/json': {
                    'example': {
                        'id': 1,
                        'first_name': 'Jean',
                        'last_name': 'Dupont',
                        'canton': 'Golfe 1',
                        'specialisations': ['Cultures vivrières', 'Irrigation'],
                        'rating': 4.5,
                        'missions_completed': 15,
                        'disponible': True,
                        'tarif_horaire': 5000
                    }
                }
            }
        ),
        401: OpenApiResponse(description='Non authentifié'),
        404: OpenApiResponse(description='Agronome non trouvé')
    },
    tags=['Agronomes']
)


# ============================================
# DOCUMENTATION: Vérification des Exploitations
# ============================================

farm_verification_request_schema = extend_schema(
    summary="Demander la vérification d'une exploitation",
    description="""
    Soumet une demande de vérification pour une exploitation agricole.
    
    **Documents requis**:
    - Preuve de propriété ou bail
    - Photos de l'exploitation
    - Coordonnées GPS
    
    **Accès**: Exploitants uniquement
    """,
    request={
        'multipart/form-data': {
            'example': {
                'farm_name': 'Ferme de Kpalimé',
                'surface_hectares': 5.5,
                'latitude': 6.9,
                'longitude': 0.6,
                'documents': '<binary>'
            }
        }
    },
    responses={
        201: OpenApiResponse(description='Demande soumise'),
        400: OpenApiResponse(description='Données invalides'),
        403: OpenApiResponse(description='Accès refusé (non exploitant)')
    },
    tags=['Exploitations']
)


farm_verification_status_schema = extend_schema(
    summary="Statut de vérification de l'exploitation",
    description="""
    Retourne le statut de vérification de l'exploitation de l'utilisateur.
    
    **Statuts possibles**:
    - EN_ATTENTE: Demande en cours d'examen
    - VALIDE: Exploitation vérifiée
    - REJETE: Demande rejetée
    """,
    responses={
        200: OpenApiResponse(
            description='Statut de vérification',
            response={
                'application/json': {
                    'example': {
                        'status': 'VALIDE',
                        'verified': True,
                        'verified_at': '2024-01-20T15:00:00Z'
                    }
                }
            }
        ),
        404: OpenApiResponse(description='Aucune demande trouvée')
    },
    tags=['Exploitations']
)


verify_farm_schema = extend_schema(
    summary="Valider une exploitation (Admin)",
    description="""
    Valide ou rejette une demande de vérification d'exploitation.
    
    **Accès**: Administrateurs uniquement
    """,
    request={
        'application/json': {
            'example': {
                'approved': True,
                'motif_rejet': 'Documents incomplets'
            }
        }
    },
    responses={
        200: OpenApiResponse(description='Validation effectuée'),
        400: OpenApiResponse(description='Paramètres invalides'),
        403: OpenApiResponse(description='Accès refusé'),
        404: OpenApiResponse(description='Exploitation non trouvée')
    },
    tags=['Exploitations']
)


get_pending_farms_schema = extend_schema(
    summary="Liste des exploitations en attente (Admin)",
    description="""
    Retourne la liste des exploitations en attente de validation.
    
    **Accès**: Administrateurs uniquement
    """,
    responses={
        200: OpenApiResponse(
            description='Liste des exploitations en attente',
            response={
                'application/json': {
                    'example': {
                        'count': 3,
                        'farms': [
                            {
                                'id': 1,
                                'farm_name': 'Ferme de Kpalimé',
                                'owner': 'Jean Dupont',
                                'surface_hectares': 5.5,
                                'submitted_at': '2024-01-15T10:30:00Z'
                            }
                        ]
                    }
                }
            }
        ),
        403: OpenApiResponse(description='Accès refusé')
    },
    tags=['Exploitations']
)


get_farm_details_schema = extend_schema(
    summary="Détails d'une exploitation (Admin)",
    description="""
    Retourne les détails complets d'une exploitation incluant documents.
    
    **Accès**: Administrateurs uniquement
    """,
    responses={
        200: OpenApiResponse(description='Détails de l\'exploitation'),
        403: OpenApiResponse(description='Accès refusé'),
        404: OpenApiResponse(description='Exploitation non trouvée')
    },
    tags=['Exploitations']
)


farm_premium_features_schema = extend_schema(
    summary="Fonctionnalités premium pour exploitations vérifiées",
    description="""
    Retourne les fonctionnalités premium disponibles pour les exploitations vérifiées.
    
    **Fonctionnalités**:
    - Contact direct avec agronomes
    - Préventes de production
    - Statistiques avancées
    - Support prioritaire
    """,
    responses={
        200: OpenApiResponse(
            description='Fonctionnalités premium',
            response={
                'application/json': {
                    'example': {
                        'verified': True,
                        'features': {
                            'contact_agronomists': True,
                            'presales': True,
                            'advanced_stats': True,
                            'priority_support': True
                        }
                    }
                }
            }
        ),
        403: OpenApiResponse(description='Exploitation non vérifiée')
    },
    tags=['Exploitations']
)


# ============================================
# DOCUMENTATION: Échange de Neon
# ============================================

neon_exchange_schema = extend_schema(
    summary="Échanger des Neon contre des FCFA",
    description="""
    Permet aux utilisateurs d'échanger leurs Neon (points de fidélité) contre des FCFA.
    
    **Taux de conversion**: 1 Neon = 10 FCFA
    
    **Minimum**: 100 Neon (1000 FCFA)
    
    **Délai de traitement**: 24-48h
    """,
    request={
        'application/json': {
            'example': {
                'neon_amount': 500,
                'mobile_money_number': '+22890123456',
                'mobile_money_provider': 'TMONEY'
            }
        }
    },
    responses={
        200: OpenApiResponse(
            description='Demande d\'échange créée',
            response={
                'application/json': {
                    'example': {
                        'message': 'Demande d\'échange créée',
                        'exchange': {
                            'neon_amount': 500,
                            'fcfa_amount': 5000,
                            'status': 'PENDING',
                            'estimated_completion': '2024-01-17T10:00:00Z'
                        }
                    }
                }
            }
        ),
        400: OpenApiResponse(description='Solde Neon insuffisant ou montant invalide'),
        401: OpenApiResponse(description='Non authentifié')
    },
    tags=['Neon']
)
