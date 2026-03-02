"""
Service de validation GPS pour les exploitations agricoles
Exigences: 10.4
"""
import math
from typing import Dict, Tuple, Optional


class GPSValidationService:
    """
    Service pour valider la cohérence entre les coordonnées GPS et la superficie déclarée
    """
    
    # Constantes pour les calculs
    EARTH_RADIUS_KM = 6371.0  # Rayon de la Terre en kilomètres
    MIN_SUPERFICIE_HECTARES = 10.0  # Superficie minimale requise
    TOLERANCE_PERCENTAGE = 0.30  # Tolérance de 30% pour la validation
    
    @staticmethod
    def validate_minimum_superficie(superficie: float) -> Tuple[bool, Optional[str]]:
        """
        Valide que la superficie respecte le minimum requis (10 hectares)
        
        Args:
            superficie: Superficie en hectares
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if superficie < GPSValidationService.MIN_SUPERFICIE_HECTARES:
            return False, f"La superficie doit être d'au moins {GPSValidationService.MIN_SUPERFICIE_HECTARES} hectares"
        return True, None
    
    @staticmethod
    def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcule la distance entre deux points GPS en kilomètres (formule de Haversine)
        
        Args:
            lat1, lon1: Coordonnées du premier point
            lat2, lon2: Coordonnées du second point
            
        Returns:
            Distance en kilomètres
        """
        # Conversion en radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Différences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Formule de Haversine
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return GPSValidationService.EARTH_RADIUS_KM * c
    
    @staticmethod
    def estimate_area_from_coordinates(coordinates: list) -> float:
        """
        Estime la superficie approximative à partir d'une liste de coordonnées GPS
        Utilise la formule de Shoelace pour calculer l'aire d'un polygone
        
        Args:
            coordinates: Liste de dictionnaires avec 'lat' et 'lon'
                        Exemple: [{'lat': 6.1, 'lon': 1.2}, {'lat': 6.2, 'lon': 1.3}, ...]
            
        Returns:
            Superficie estimée en hectares
        """
        if len(coordinates) < 3:
            return 0.0
        
        # Conversion des coordonnées en mètres (approximation locale)
        # 1 degré de latitude ≈ 111 km
        # 1 degré de longitude ≈ 111 km * cos(latitude)
        
        # Utiliser la latitude moyenne pour la conversion
        avg_lat = sum(coord['lat'] for coord in coordinates) / len(coordinates)
        lat_to_m = 111000  # mètres par degré de latitude
        lon_to_m = 111000 * math.cos(math.radians(avg_lat))  # mètres par degré de longitude
        
        # Convertir les coordonnées en mètres
        points_m = [
            (coord['lon'] * lon_to_m, coord['lat'] * lat_to_m)
            for coord in coordinates
        ]
        
        # Formule de Shoelace pour calculer l'aire
        area_m2 = 0.0
        n = len(points_m)
        for i in range(n):
            j = (i + 1) % n
            area_m2 += points_m[i][0] * points_m[j][1]
            area_m2 -= points_m[j][0] * points_m[i][1]
        
        area_m2 = abs(area_m2) / 2.0
        
        # Convertir en hectares (1 hectare = 10,000 m²)
        area_hectares = area_m2 / 10000.0
        
        return area_hectares
    
    @staticmethod
    def validate_gps_superficie_coherence(
        declared_superficie: float,
        gps_coordinates: Dict
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Valide la cohérence entre la superficie déclarée et les coordonnées GPS
        
        Args:
            declared_superficie: Superficie déclarée en hectares
            gps_coordinates: Coordonnées GPS (peut être un point ou un polygone)
                           Format point: {'lat': 6.1, 'lon': 1.2}
                           Format polygone: {'type': 'polygon', 'coordinates': [...]}
            
        Returns:
            Tuple (is_valid, error_message, validation_details)
        """
        # Valider d'abord la superficie minimale
        is_valid_min, error_min = GPSValidationService.validate_minimum_superficie(declared_superficie)
        if not is_valid_min:
            return False, error_min, None
        
        # Si c'est juste un point GPS (pas de polygone), on ne peut pas valider la superficie
        # On considère que c'est valide mais on note qu'il n'y a pas de validation de superficie
        if 'type' not in gps_coordinates or gps_coordinates.get('type') != 'polygon':
            return True, None, {
                'validation_type': 'point_only',
                'message': 'Validation basée sur un point GPS uniquement, superficie non vérifiable',
                'declared_superficie': declared_superficie
            }
        
        # Si c'est un polygone, calculer la superficie estimée
        polygon_coords = gps_coordinates.get('coordinates', [])
        if len(polygon_coords) < 3:
            return False, "Le polygone doit avoir au moins 3 points", None
        
        estimated_superficie = GPSValidationService.estimate_area_from_coordinates(polygon_coords)
        
        # Calculer la différence en pourcentage
        difference = abs(estimated_superficie - declared_superficie)
        percentage_diff = (difference / declared_superficie) * 100
        
        # Valider avec tolérance
        is_coherent = percentage_diff <= (GPSValidationService.TOLERANCE_PERCENTAGE * 100)
        
        validation_details = {
            'validation_type': 'polygon',
            'declared_superficie': declared_superficie,
            'estimated_superficie': round(estimated_superficie, 2),
            'difference_hectares': round(difference, 2),
            'percentage_difference': round(percentage_diff, 2),
            'tolerance_percentage': GPSValidationService.TOLERANCE_PERCENTAGE * 100,
            'is_coherent': is_coherent
        }
        
        if not is_coherent:
            error_message = (
                f"La superficie estimée ({estimated_superficie:.2f} ha) diffère de plus de "
                f"{GPSValidationService.TOLERANCE_PERCENTAGE * 100}% de la superficie déclarée "
                f"({declared_superficie:.2f} ha). Différence: {percentage_diff:.2f}%"
            )
            return False, error_message, validation_details
        
        return True, None, validation_details
    
    @staticmethod
    def validate_coordinates_in_togo(lat: float, lon: float) -> Tuple[bool, Optional[str]]:
        """
        Valide que les coordonnées GPS sont bien situées au Togo
        
        Limites approximatives du Togo:
        - Latitude: 6.0° N à 11.1° N
        - Longitude: 0.0° E à 1.8° E
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Tuple (is_valid, error_message)
        """
        TOGO_LAT_MIN = 6.0
        TOGO_LAT_MAX = 11.1
        TOGO_LON_MIN = 0.0
        TOGO_LON_MAX = 1.8
        
        if not (TOGO_LAT_MIN <= lat <= TOGO_LAT_MAX):
            return False, f"La latitude {lat} est en dehors des limites du Togo ({TOGO_LAT_MIN}° - {TOGO_LAT_MAX}°)"
        
        if not (TOGO_LON_MIN <= lon <= TOGO_LON_MAX):
            return False, f"La longitude {lon} est en dehors des limites du Togo ({TOGO_LON_MIN}° - {TOGO_LON_MAX}°)"
        
        return True, None
    
    @staticmethod
    def validate_farm_verification_request(
        superficie: float,
        gps_coordinates: Dict
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Validation complète d'une demande de vérification d'exploitation
        
        Args:
            superficie: Superficie déclarée en hectares
            gps_coordinates: Coordonnées GPS
            
        Returns:
            Tuple (is_valid, error_message, validation_details)
        """
        # 1. Valider la superficie minimale
        is_valid_min, error_min = GPSValidationService.validate_minimum_superficie(superficie)
        if not is_valid_min:
            return False, error_min, None
        
        # 2. Valider que les coordonnées sont au Togo
        if 'lat' in gps_coordinates and 'lon' in gps_coordinates:
            is_valid_togo, error_togo = GPSValidationService.validate_coordinates_in_togo(
                gps_coordinates['lat'],
                gps_coordinates['lon']
            )
            if not is_valid_togo:
                return False, error_togo, None
        
        # 3. Valider la cohérence GPS/superficie
        is_coherent, error_coherence, details = GPSValidationService.validate_gps_superficie_coherence(
            superficie,
            gps_coordinates
        )
        
        return is_coherent, error_coherence, details
