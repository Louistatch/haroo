"""
Serializers pour l'authentification et les utilisateurs
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .services import PasswordValidationService
from .file_upload import FileUploadService

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """Serializer pour l'inscription d'un nouvel utilisateur"""
    
    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text="Nom d'utilisateur unique"
    )
    email = serializers.EmailField(
        required=True,
        help_text="Adresse email"
    )
    phone_number = serializers.CharField(
        max_length=15,
        required=True,
        help_text="Numéro de téléphone togolais (format: +228XXXXXXXX)"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Mot de passe (min 8 caractères, 1 majuscule, 1 chiffre, 1 caractère spécial)"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirmation du mot de passe"
    )
    user_type = serializers.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        help_text="Type de profil utilisateur"
    )
    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True
    )
    
    def validate_username(self, value):
        """Vérifie que le nom d'utilisateur est unique"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà utilisé")
        return value
    
    def validate_email(self, value):
        """Vérifie que l'email est unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cette adresse email est déjà utilisée")
        return value
    
    def validate_phone_number(self, value):
        """Vérifie que le numéro de téléphone est valide et unique"""
        # Vérifier le format togolais
        if not value.startswith('+228'):
            raise serializers.ValidationError(
                "Le numéro doit être un numéro togolais (format: +228XXXXXXXX)"
            )
        
        if len(value) != 12:  # +228 + 8 chiffres
            raise serializers.ValidationError(
                "Le numéro de téléphone doit contenir 8 chiffres après +228"
            )
        
        # Vérifier l'unicité
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Ce numéro de téléphone est déjà utilisé")
        
        return value
    
    def validate_password(self, value):
        """Valide le mot de passe selon les critères de sécurité"""
        validation_result = PasswordValidationService.validate_password(value)
        
        if not validation_result['is_valid']:
            raise serializers.ValidationError(validation_result['errors'])
        
        return value
    
    def validate(self, attrs):
        """Validation globale"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Les mots de passe ne correspondent pas"
            })
        
        return attrs
    
    def create(self, validated_data):
        """Crée un nouvel utilisateur"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion"""
    
    phone_number = serializers.CharField(
        required=True,
        help_text="Numéro de téléphone"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Mot de passe"
    )


class VerifySMSSerializer(serializers.Serializer):
    """Serializer pour la vérification du code SMS"""
    
    phone_number = serializers.CharField(
        required=True,
        help_text="Numéro de téléphone"
    )
    code = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text="Code de vérification à 6 chiffres"
    )


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer pour le rafraîchissement du token"""
    
    refresh_token = serializers.CharField(
        required=True,
        help_text="Token de rafraîchissement"
    )


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les informations utilisateur"""
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'phone_number',
            'phone_verified',
            'user_type',
            'first_name',
            'last_name',
            'two_factor_enabled',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'phone_verified',
            'two_factor_enabled',
            'created_at',
            'updated_at'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour le changement de mot de passe"""
    
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_new_password(self, value):
        """Valide le nouveau mot de passe"""
        validation_result = PasswordValidationService.validate_password(value)
        
        if not validation_result['is_valid']:
            raise serializers.ValidationError(validation_result['errors'])
        
        return value
    
    def validate(self, attrs):
        """Validation globale"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Les mots de passe ne correspondent pas"
            })
        
        return attrs


class ExploitantProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil exploitant"""
    canton_principal_nom = serializers.CharField(source='canton_principal.nom', read_only=True)
    
    class Meta:
        from .models import ExploitantProfile
        model = ExploitantProfile
        fields = [
            'superficie_totale',
            'canton_principal',
            'canton_principal_nom',
            'coordonnees_gps',
            'statut_verification',
            'date_verification',
            'cultures_actuelles'
        ]
        read_only_fields = ['statut_verification', 'date_verification']


class AgronomeProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil agronome"""
    canton_rattachement_nom = serializers.CharField(source='canton_rattachement.nom', read_only=True)
    
    class Meta:
        from .models import AgronomeProfile
        model = AgronomeProfile
        fields = [
            'canton_rattachement',
            'canton_rattachement_nom',
            'specialisations',
            'statut_validation',
            'badge_valide',
            'date_validation',
            'motif_rejet',
            'note_moyenne',
            'nombre_avis'
        ]
        read_only_fields = ['statut_validation', 'badge_valide', 'date_validation', 'motif_rejet', 'note_moyenne', 'nombre_avis']


class DocumentJustificatifSerializer(serializers.ModelSerializer):
    """Serializer pour les documents justificatifs"""
    
    class Meta:
        from .models import DocumentJustificatif
        model = DocumentJustificatif
        fields = [
            'id',
            'type_document',
            'fichier',
            'nom_fichier',
            'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']
    
    def validate_fichier(self, value):
        """
        Valide le fichier uploadé
        Exigences: 31.1, 31.2, 31.5, 31.6
        """
        if value:
            validation_result = FileUploadService.validate_document_file(value)
            if not validation_result['is_valid']:
                raise serializers.ValidationError(validation_result['errors'])
        return value


class AgronomeRegistrationSerializer(serializers.Serializer):
    """
    Serializer pour l'inscription d'un agronome
    Exigences: 7.1, 7.2, 7.3, 7.4
    """
    # Informations utilisateur de base
    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text="Nom d'utilisateur unique"
    )
    email = serializers.EmailField(
        required=True,
        help_text="Adresse email"
    )
    phone_number = serializers.CharField(
        max_length=15,
        required=True,
        help_text="Numéro de téléphone togolais (format: +228XXXXXXXX)"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Mot de passe"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirmation du mot de passe"
    )
    first_name = serializers.CharField(
        max_length=150,
        required=True,
        help_text="Prénom"
    )
    last_name = serializers.CharField(
        max_length=150,
        required=True,
        help_text="Nom de famille"
    )
    
    # Informations spécifiques à l'agronome
    canton_rattachement = serializers.IntegerField(
        required=True,
        help_text="ID du canton de rattachement"
    )
    specialisations = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=True,
        min_length=1,
        help_text="Liste des spécialisations agricoles"
    )
    
    # Documents justificatifs (optionnels à l'inscription, peuvent être ajoutés après)
    documents = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True,
        help_text="Documents justificatifs (diplômes, certifications, pièce d'identité)"
    )
    types_documents = serializers.ListField(
        child=serializers.ChoiceField(choices=['DIPLOME', 'CERTIFICATION', 'PIECE_IDENTITE', 'AUTRE']),
        required=False,
        allow_empty=True,
        help_text="Types des documents (doit correspondre à la liste des documents)"
    )
    
    # Liste des spécialisations disponibles
    SPECIALISATIONS_DISPONIBLES = [
        'Cultures céréalières',
        'Cultures maraîchères',
        'Arboriculture fruitière',
        'Cultures industrielles',
        'Élevage bovin',
        'Élevage porcin',
        'Aviculture',
        'Pisciculture',
        'Agroforesterie',
        'Agriculture biologique',
        'Irrigation',
        'Mécanisation agricole',
        'Protection des cultures',
        'Fertilisation des sols',
        'Gestion post-récolte',
    ]
    
    def validate_username(self, value):
        """Vérifie que le nom d'utilisateur est unique"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà utilisé")
        return value
    
    def validate_email(self, value):
        """Vérifie que l'email est unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cette adresse email est déjà utilisée")
        return value
    
    def validate_phone_number(self, value):
        """Vérifie que le numéro de téléphone est valide et unique"""
        if not value.startswith('+228'):
            raise serializers.ValidationError(
                "Le numéro doit être un numéro togolais (format: +228XXXXXXXX)"
            )
        
        if len(value) != 12:
            raise serializers.ValidationError(
                "Le numéro de téléphone doit contenir 8 chiffres après +228"
            )
        
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Ce numéro de téléphone est déjà utilisé")
        
        return value
    
    def validate_password(self, value):
        """Valide le mot de passe selon les critères de sécurité"""
        validation_result = PasswordValidationService.validate_password(value)
        
        if not validation_result['is_valid']:
            raise serializers.ValidationError(validation_result['errors'])
        
        return value
    
    def validate_canton_rattachement(self, value):
        """Vérifie que le canton existe"""
        from apps.locations.models import Canton
        
        if not Canton.objects.filter(id=value).exists():
            raise serializers.ValidationError("Canton invalide")
        
        return value
    
    def validate_specialisations(self, value):
        """
        Vérifie que les spécialisations sont valides
        Exigence: 7.2
        """
        if not value:
            raise serializers.ValidationError("Au moins une spécialisation est requise")
        
        # Vérifier que toutes les spécialisations sont dans la liste prédéfinie
        invalid_specs = [spec for spec in value if spec not in self.SPECIALISATIONS_DISPONIBLES]
        if invalid_specs:
            raise serializers.ValidationError(
                f"Spécialisations invalides: {', '.join(invalid_specs)}. "
                f"Spécialisations disponibles: {', '.join(self.SPECIALISATIONS_DISPONIBLES)}"
            )
        
        return value
    
    def validate_documents(self, value):
        """
        Valide les documents uploadés
        Exigence: 7.4, 31.1, 31.2, 31.5, 31.6
        """
        if value:
            for document in value:
                validation_result = FileUploadService.validate_document_file(document)
                if not validation_result['is_valid']:
                    raise serializers.ValidationError(
                        f"Fichier {document.name}: {', '.join(validation_result['errors'])}"
                    )
        return value
    
    def validate(self, attrs):
        """Validation globale"""
        # Vérifier que les mots de passe correspondent
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Les mots de passe ne correspondent pas"
            })
        
        # Vérifier que le nombre de types de documents correspond au nombre de documents
        documents = attrs.get('documents', [])
        types_documents = attrs.get('types_documents', [])
        
        if documents and types_documents:
            if len(documents) != len(types_documents):
                raise serializers.ValidationError({
                    'types_documents': "Le nombre de types de documents doit correspondre au nombre de documents"
                })
        
        return attrs


class OuvrierProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil ouvrier"""
    
    class Meta:
        from .models import OuvrierProfile
        model = OuvrierProfile
        fields = [
            'competences',
            'cantons_disponibles',
            'note_moyenne',
            'nombre_avis',
            'disponible'
        ]
        read_only_fields = ['note_moyenne', 'nombre_avis']


class AcheteurProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil acheteur"""
    
    class Meta:
        from .models import AcheteurProfile
        model = AcheteurProfile
        fields = [
            'type_acheteur',
            'volume_achats_annuel'
        ]


class InstitutionProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil institution"""
    
    class Meta:
        from .models import InstitutionProfile
        model = InstitutionProfile
        fields = [
            'nom_organisme',
            'niveau_acces',
            'regions_acces'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer complet pour l'utilisateur avec son profil spécifique"""
    exploitant_profile = ExploitantProfileSerializer(required=False)
    agronome_profile = AgronomeProfileSerializer(required=False)
    ouvrier_profile = OuvrierProfileSerializer(required=False)
    acheteur_profile = AcheteurProfileSerializer(required=False)
    institution_profile = InstitutionProfileSerializer(required=False)
    photo_profil = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'phone_number',
            'phone_verified',
            'user_type',
            'first_name',
            'last_name',
            'two_factor_enabled',
            'photo_profil',
            'exploitant_profile',
            'agronome_profile',
            'ouvrier_profile',
            'acheteur_profile',
            'institution_profile',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'phone_verified',
            'two_factor_enabled',
            'created_at',
            'updated_at'
        ]
    
    def validate_photo_profil(self, value):
        """
        Valide la photo de profil uploadée
        Exigences: 31.1, 31.2, 31.5
        """
        if value:
            validation_result = FileUploadService.validate_image_file(value)
            if not validation_result['is_valid']:
                raise serializers.ValidationError(validation_result['errors'])
        return value
    
    def update(self, instance, validated_data):
        """Met à jour l'utilisateur et son profil spécifique"""
        # Extraire les données de profil
        profile_data = None
        profile_field = None
        
        if instance.user_type == 'EXPLOITANT' and 'exploitant_profile' in validated_data:
            profile_data = validated_data.pop('exploitant_profile')
            profile_field = 'exploitant_profile'
        elif instance.user_type == 'AGRONOME' and 'agronome_profile' in validated_data:
            profile_data = validated_data.pop('agronome_profile')
            profile_field = 'agronome_profile'
        elif instance.user_type == 'OUVRIER' and 'ouvrier_profile' in validated_data:
            profile_data = validated_data.pop('ouvrier_profile')
            profile_field = 'ouvrier_profile'
        elif instance.user_type == 'ACHETEUR' and 'acheteur_profile' in validated_data:
            profile_data = validated_data.pop('acheteur_profile')
            profile_field = 'acheteur_profile'
        elif instance.user_type == 'INSTITUTION' and 'institution_profile' in validated_data:
            profile_data = validated_data.pop('institution_profile')
            profile_field = 'institution_profile'
        
        # Mettre à jour les champs de base de l'utilisateur
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour le profil spécifique si des données sont fournies
        if profile_data and profile_field:
            profile = getattr(instance, profile_field, None)
            if profile:
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save()
        
        return instance



class Setup2FASerializer(serializers.Serializer):
    """Serializer pour la configuration initiale du 2FA"""
    pass  # Pas de champs requis, utilise l'utilisateur authentifié


class Enable2FASerializer(serializers.Serializer):
    """Serializer pour l'activation du 2FA"""
    token = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text="Code à 6 chiffres de votre application d'authentification"
    )
    
    def validate_token(self, value):
        """Vérifie que le token contient uniquement des chiffres"""
        if not value.isdigit():
            raise serializers.ValidationError("Le token doit contenir uniquement des chiffres")
        return value


class Disable2FASerializer(serializers.Serializer):
    """Serializer pour la désactivation du 2FA"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Mot de passe pour confirmation"
    )


class Verify2FASerializer(serializers.Serializer):
    """Serializer pour la vérification du token 2FA lors de la connexion"""
    phone_number = serializers.CharField(
        required=True,
        help_text="Numéro de téléphone"
    )
    token = serializers.CharField(
        required=True,
        max_length=8,
        help_text="Code à 6 chiffres de votre application d'authentification ou code de secours à 8 caractères"
    )
    
    def validate_token(self, value):
        """Vérifie le format du token"""
        # Accepter soit un token TOTP (6 chiffres) soit un code de secours (8 caractères alphanumériques)
        if len(value) == 6 and not value.isdigit():
            raise serializers.ValidationError("Le token TOTP doit contenir uniquement des chiffres")
        elif len(value) != 6 and len(value) != 8:
            raise serializers.ValidationError("Le token doit contenir 6 chiffres (TOTP) ou 8 caractères (code de secours)")
        return value


class AgronomeDirectorySerializer(serializers.ModelSerializer):
    """
    Serializer pour l'annuaire public des agronomes validés
    Exigences: 8.1, 8.2, 8.3, 8.4
    """
    # Informations utilisateur
    nom_complet = serializers.SerializerMethodField()
    
    # Informations de localisation
    canton_nom = serializers.CharField(source='canton_rattachement.nom', read_only=True)
    prefecture_nom = serializers.CharField(source='canton_rattachement.prefecture.nom', read_only=True)
    region_nom = serializers.CharField(source='canton_rattachement.prefecture.region.nom', read_only=True)
    
    class Meta:
        from .models import AgronomeProfile
        model = AgronomeProfile
        fields = [
            'id',
            'nom_complet',
            'specialisations',
            'canton_nom',
            'prefecture_nom',
            'region_nom',
            'note_moyenne',
            'nombre_avis',
            'badge_valide'
        ]
    
    def get_nom_complet(self, obj):
        """Retourne le nom complet de l'agronome"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username



class FarmVerificationDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer pour les documents de vérification d'exploitation
    Exigences: 10.3, 31.1, 31.3
    """
    
    class Meta:
        from .models import FarmVerificationDocument
        model = FarmVerificationDocument
        fields = [
            'id',
            'type_document',
            'fichier',
            'nom_fichier',
            'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']
    
    def validate_fichier(self, value):
        """
        Valide le fichier uploadé
        Exigences: 31.1, 31.2, 31.5, 31.6
        """
        if value:
            validation_result = FileUploadService.validate_document_file(value)
            if not validation_result['is_valid']:
                raise serializers.ValidationError(validation_result['errors'])
        return value


class FarmVerificationRequestSerializer(serializers.Serializer):
    """
    Serializer pour la demande de vérification d'exploitation
    Exigences: 10.1, 10.2, 10.3, 10.4
    """
    superficie_totale = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        help_text="Superficie totale de l'exploitation en hectares (minimum 10 ha)"
    )
    canton_principal = serializers.IntegerField(
        required=True,
        help_text="ID du canton principal de l'exploitation"
    )
    coordonnees_gps = serializers.JSONField(
        required=True,
        help_text="Coordonnées GPS (point ou polygone). Format point: {'lat': 6.1, 'lon': 1.2}. Format polygone: {'type': 'polygon', 'coordinates': [{'lat': 6.1, 'lon': 1.2}, ...]}"
    )
    cultures_actuelles = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True,
        help_text="Liste des cultures actuellement cultivées"
    )
    
    # Documents justificatifs
    documents = serializers.ListField(
        child=serializers.FileField(),
        required=True,
        min_length=1,
        help_text="Documents justificatifs (titre foncier, certificat d'exploitation, photos aériennes)"
    )
    types_documents = serializers.ListField(
        child=serializers.ChoiceField(choices=['TITRE_FONCIER', 'CERTIFICAT_EXPLOITATION', 'PHOTO_AERIENNE', 'AUTRE']),
        required=True,
        min_length=1,
        help_text="Types des documents (doit correspondre à la liste des documents)"
    )
    
    def validate_superficie_totale(self, value):
        """
        Valide que la superficie respecte le minimum requis
        Exigence: 10.2
        """
        from .gps_validation import GPSValidationService
        
        is_valid, error_message = GPSValidationService.validate_minimum_superficie(float(value))
        if not is_valid:
            raise serializers.ValidationError(error_message)
        
        return value
    
    def validate_canton_principal(self, value):
        """Vérifie que le canton existe"""
        from apps.locations.models import Canton
        
        if not Canton.objects.filter(id=value).exists():
            raise serializers.ValidationError("Canton invalide")
        
        return value
    
    def validate_coordonnees_gps(self, value):
        """
        Valide les coordonnées GPS
        Exigence: 10.4
        """
        from .gps_validation import GPSValidationService
        
        # Vérifier le format
        if 'lat' not in value or 'lon' not in value:
            if 'type' not in value or value.get('type') != 'polygon':
                raise serializers.ValidationError(
                    "Les coordonnées GPS doivent contenir 'lat' et 'lon' pour un point, "
                    "ou 'type': 'polygon' et 'coordinates' pour un polygone"
                )
        
        # Valider que les coordonnées sont au Togo
        if 'lat' in value and 'lon' in value:
            try:
                lat = float(value['lat'])
                lon = float(value['lon'])
                is_valid, error_message = GPSValidationService.validate_coordinates_in_togo(lat, lon)
                if not is_valid:
                    raise serializers.ValidationError(error_message)
            except (ValueError, TypeError):
                raise serializers.ValidationError("Les coordonnées GPS doivent être des nombres valides")
        
        # Valider le polygone si présent
        if value.get('type') == 'polygon':
            coordinates = value.get('coordinates', [])
            if len(coordinates) < 3:
                raise serializers.ValidationError("Un polygone doit avoir au moins 3 points")
            
            # Valider chaque point du polygone
            for i, coord in enumerate(coordinates):
                if 'lat' not in coord or 'lon' not in coord:
                    raise serializers.ValidationError(
                        f"Le point {i+1} du polygone doit contenir 'lat' et 'lon'"
                    )
                try:
                    lat = float(coord['lat'])
                    lon = float(coord['lon'])
                    is_valid, error_message = GPSValidationService.validate_coordinates_in_togo(lat, lon)
                    if not is_valid:
                        raise serializers.ValidationError(f"Point {i+1}: {error_message}")
                except (ValueError, TypeError):
                    raise serializers.ValidationError(
                        f"Le point {i+1} du polygone doit avoir des coordonnées numériques valides"
                    )
        
        return value
    
    def validate_documents(self, value):
        """
        Valide les documents uploadés
        Exigence: 10.3, 31.1, 31.2, 31.5, 31.6
        """
        if value:
            for document in value:
                validation_result = FileUploadService.validate_document_file(document)
                if not validation_result['is_valid']:
                    raise serializers.ValidationError(
                        f"Fichier {document.name}: {', '.join(validation_result['errors'])}"
                    )
        return value
    
    def validate(self, attrs):
        """
        Validation globale incluant la cohérence GPS/superficie
        Exigence: 10.4
        """
        from .gps_validation import GPSValidationService
        
        # Vérifier que le nombre de types de documents correspond au nombre de documents
        documents = attrs.get('documents', [])
        types_documents = attrs.get('types_documents', [])
        
        if len(documents) != len(types_documents):
            raise serializers.ValidationError({
                'types_documents': "Le nombre de types de documents doit correspondre au nombre de documents"
            })
        
        # Valider la cohérence GPS/superficie
        superficie = float(attrs['superficie_totale'])
        coordonnees_gps = attrs['coordonnees_gps']
        
        is_valid, error_message, validation_details = GPSValidationService.validate_farm_verification_request(
            superficie,
            coordonnees_gps
        )
        
        if not is_valid:
            raise serializers.ValidationError({
                'coordonnees_gps': error_message
            })
        
        # Stocker les détails de validation pour utilisation ultérieure
        attrs['_validation_details'] = validation_details
        
        return attrs


class FarmVerificationStatusSerializer(serializers.ModelSerializer):
    """
    Serializer pour afficher le statut de vérification d'une exploitation
    Exigences: 10.4, 10.5
    """
    canton_principal_nom = serializers.CharField(source='canton_principal.nom', read_only=True)
    prefecture_nom = serializers.CharField(source='canton_principal.prefecture.nom', read_only=True)
    region_nom = serializers.CharField(source='canton_principal.prefecture.region.nom', read_only=True)
    documents_verification = FarmVerificationDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        from .models import ExploitantProfile
        model = ExploitantProfile
        fields = [
            'superficie_totale',
            'canton_principal',
            'canton_principal_nom',
            'prefecture_nom',
            'region_nom',
            'coordonnees_gps',
            'statut_verification',
            'date_verification',
            'motif_rejet',
            'cultures_actuelles',
            'documents_verification'
        ]
        read_only_fields = [
            'statut_verification',
            'date_verification',
            'motif_rejet',
            'documents_verification'
        ]
