"""
Service de gestion des sessions utilisateur

Exigences: 40.1, 40.2, 40.3, 40.4, 40.5
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
import hashlib
import re

User = get_user_model()


class SessionManagementService:
    """
    Service pour la gestion avancée des sessions utilisateur
    
    Fonctionnalités:
    - Stockage des sessions dans Redis avec TTL de 24h
    - Invalidation de tokens lors de la déconnexion
    - Déconnexion multi-appareils
    - Affichage des sessions actives avec informations détaillées
    """
    
    SESSION_TTL = 86400  # 24 heures en secondes
    
    @staticmethod
    def _get_session_key(user_id: int, token_hash: str) -> str:
        """Génère une clé de session unique"""
        return f"session:{user_id}:{token_hash}"
    
    @staticmethod
    def _get_user_sessions_key(user_id: int) -> str:
        """Génère une clé pour la liste des sessions d'un utilisateur"""
        return f"user_sessions:{user_id}"
    
    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash un token JWT pour le stockage"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def _parse_user_agent(user_agent: str) -> Dict[str, str]:
        """Parse le user agent pour extraire les informations de l'appareil"""
        device = 'Desktop'
        browser = 'Unknown'
        os = 'Unknown'
        
        if re.search(r'Mobile|Android|iPhone|iPad|iPod', user_agent, re.I):
            device = 'Mobile'
        elif re.search(r'Tablet|iPad', user_agent, re.I):
            device = 'Tablet'
        
        if 'Chrome' in user_agent and 'Edg' not in user_agent:
            browser = 'Chrome'
        elif 'Firefox' in user_agent:
            browser = 'Firefox'
        elif 'Safari' in user_agent and 'Chrome' not in user_agent:
            browser = 'Safari'
        elif 'Edg' in user_agent:
            browser = 'Edge'
        elif 'MSIE' in user_agent or 'Trident' in user_agent:
            browser = 'Internet Explorer'
        
        if 'Windows' in user_agent:
            os = 'Windows'
        elif 'Mac OS' in user_agent or 'Macintosh' in user_agent:
            os = 'macOS'
        elif 'Linux' in user_agent:
            os = 'Linux'
        elif 'Android' in user_agent:
            os = 'Android'
        elif 'iOS' in user_agent or 'iPhone' in user_agent or 'iPad' in user_agent:
            os = 'iOS'
        
        return {'device': device, 'browser': browser, 'os': os}
    
    @staticmethod
    def _get_location_from_ip(ip_address: str) -> str:
        """Obtient la localisation approximative depuis l'adresse IP"""
        if not ip_address or ip_address == 'Unknown':
            return 'Unknown'
        if ip_address.startswith('127.') or ip_address.startswith('192.168.') or ip_address.startswith('10.'):
            return 'Local'
        return 'Unknown'
    
    @staticmethod
    def create_session(user_id: int, token: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None, device_info: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Crée une nouvelle session utilisateur dans Redis - Exigences: 40.1"""
        token_hash = SessionManagementService._hash_token(token)
        session_key = SessionManagementService._get_session_key(user_id, token_hash)
        
        if not device_info and user_agent:
            device_info = SessionManagementService._parse_user_agent(user_agent)
        
        session_data = {
            'user_id': user_id,
            'token_hash': token_hash,
            'device': device_info.get('device', 'Unknown') if device_info else 'Unknown',
            'browser': device_info.get('browser', 'Unknown') if device_info else 'Unknown',
            'os': device_info.get('os', 'Unknown') if device_info else 'Unknown',
            'ip_address': ip_address or 'Unknown',
            'location': SessionManagementService._get_location_from_ip(ip_address) if ip_address else 'Unknown',
            'created_at': timezone.now().isoformat(),
            'last_activity': timezone.now().isoformat(),
        }
        
        cache.set(session_key, session_data, timeout=SessionManagementService.SESSION_TTL)
        
        user_sessions_key = SessionManagementService._get_user_sessions_key(user_id)
        user_sessions = cache.get(user_sessions_key, [])
        
        if token_hash not in user_sessions:
            user_sessions.append(token_hash)
            cache.set(user_sessions_key, user_sessions, timeout=SessionManagementService.SESSION_TTL)
        
        return session_data
    
    @staticmethod
    def update_session_activity(user_id: int, token: str) -> bool:
        """Met à jour l'activité d'une session - Exigences: 40.1"""
        token_hash = SessionManagementService._hash_token(token)
        session_key = SessionManagementService._get_session_key(user_id, token_hash)
        
        session_data = cache.get(session_key)
        
        if not session_data:
            return False
        
        session_data['last_activity'] = timezone.now().isoformat()
        cache.set(session_key, session_data, timeout=SessionManagementService.SESSION_TTL)
        
        user_sessions_key = SessionManagementService._get_user_sessions_key(user_id)
        user_sessions = cache.get(user_sessions_key, [])
        if user_sessions:
            cache.set(user_sessions_key, user_sessions, timeout=SessionManagementService.SESSION_TTL)
        
        return True
    
    @staticmethod
    def invalidate_session(user_id: int, token: str) -> bool:
        """Invalide une session spécifique (déconnexion) - Exigences: 40.2"""
        token_hash = SessionManagementService._hash_token(token)
        session_key = SessionManagementService._get_session_key(user_id, token_hash)
        
        cache.delete(session_key)
        
        user_sessions_key = SessionManagementService._get_user_sessions_key(user_id)
        user_sessions = cache.get(user_sessions_key, [])
        
        if token_hash in user_sessions:
            user_sessions.remove(token_hash)
            if user_sessions:
                cache.set(user_sessions_key, user_sessions, timeout=SessionManagementService.SESSION_TTL)
            else:
                cache.delete(user_sessions_key)
            return True
        
        return False
    
    @staticmethod
    def invalidate_all_sessions(user_id: int) -> int:
        """Invalide toutes les sessions d'un utilisateur - Exigences: 40.3"""
        user_sessions_key = SessionManagementService._get_user_sessions_key(user_id)
        user_sessions = cache.get(user_sessions_key, [])
        
        count = 0
        for token_hash in user_sessions:
            session_key = SessionManagementService._get_session_key(user_id, token_hash)
            if cache.delete(session_key):
                count += 1
        
        cache.delete(user_sessions_key)
        
        return count
    
    @staticmethod
    def get_active_sessions(user_id: int) -> List[Dict[str, Any]]:
        """Récupère toutes les sessions actives d'un utilisateur - Exigences: 40.4, 40.5"""
        user_sessions_key = SessionManagementService._get_user_sessions_key(user_id)
        user_sessions = cache.get(user_sessions_key, [])
        
        active_sessions = []
        sessions_to_remove = []
        
        for token_hash in user_sessions:
            session_key = SessionManagementService._get_session_key(user_id, token_hash)
            session_data = cache.get(session_key)
            
            if session_data:
                session_info = {
                    'device': session_data.get('device', 'Unknown'),
                    'browser': session_data.get('browser', 'Unknown'),
                    'os': session_data.get('os', 'Unknown'),
                    'ip_address': session_data.get('ip_address', 'Unknown'),
                    'location': session_data.get('location', 'Unknown'),
                    'created_at': session_data.get('created_at'),
                    'last_activity': session_data.get('last_activity'),
                    'session_id': token_hash[:16]
                }
                active_sessions.append(session_info)
            else:
                sessions_to_remove.append(token_hash)
        
        if sessions_to_remove:
            user_sessions = [s for s in user_sessions if s not in sessions_to_remove]
            if user_sessions:
                cache.set(user_sessions_key, user_sessions, timeout=SessionManagementService.SESSION_TTL)
            else:
                cache.delete(user_sessions_key)
        
        active_sessions.sort(key=lambda x: x.get('last_activity', ''), reverse=True)
        
        return active_sessions
    
    @staticmethod
    def is_session_valid(user_id: int, token: str) -> bool:
        """Vérifie si une session est valide"""
        token_hash = SessionManagementService._hash_token(token)
        session_key = SessionManagementService._get_session_key(user_id, token_hash)
        return cache.get(session_key) is not None
    
    @staticmethod
    def get_session_info(user_id: int, token: str) -> Optional[Dict[str, Any]]:
        """Récupère les informations d'une session spécifique"""
        token_hash = SessionManagementService._hash_token(token)
        session_key = SessionManagementService._get_session_key(user_id, token_hash)
        
        session_data = cache.get(session_key)
        
        if not session_data:
            return None
        
        return {
            'device': session_data.get('device', 'Unknown'),
            'browser': session_data.get('browser', 'Unknown'),
            'os': session_data.get('os', 'Unknown'),
            'ip_address': session_data.get('ip_address', 'Unknown'),
            'location': session_data.get('location', 'Unknown'),
            'created_at': session_data.get('created_at'),
            'last_activity': session_data.get('last_activity'),
        }
