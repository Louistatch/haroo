"""
URLs pour l'authentification et la gestion des utilisateurs
"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentification
    path('auth/register', views.register, name='register'),
    path('auth/login', views.login, name='login'),
    path('auth/neon-exchange', views.neon_exchange, name='neon-exchange'),
    path('auth/verify-sms', views.verify_sms, name='verify-sms'),
    path('auth/resend-sms', views.resend_sms_code, name='resend-sms'),
    path('auth/refresh-token', views.refresh_token, name='refresh-token'),
    
    # 2FA - Exigences: 25.2
    path('auth/2fa/setup', views.setup_2fa, name='2fa-setup'),
    path('auth/2fa/enable', views.enable_2fa, name='2fa-enable'),
    path('auth/2fa/disable', views.disable_2fa, name='2fa-disable'),
    path('auth/2fa/verify', views.verify_2fa, name='2fa-verify'),
    path('auth/2fa/status', views.check_2fa_status, name='2fa-status'),
    
    # Profil utilisateur - Exigences: 2.5, 31.1, 31.3
    path('users/me', views.manage_profile, name='manage-profile'),  # GET & PATCH
    path('users/me/change-password', views.change_password, name='change-password'),
    
    # Gestion des sessions - Exigences: 40.1, 40.2, 40.3, 40.4, 40.5
    path('auth/logout', views.logout, name='logout'),
    path('auth/logout-all', views.logout_all_devices, name='logout-all-devices'),
    path('users/me/sessions', views.active_sessions, name='active-sessions'),
    
    # Inscription et gestion des agronomes - Exigences: 7.1, 7.2, 7.3, 7.4
    path('agronomists/register', views.register_agronomist, name='register-agronomist'),
    path('agronomists/documents/upload', views.upload_agronomist_document, name='upload-agronomist-document'),
    path('agronomists/documents', views.get_agronomist_documents, name='get-agronomist-documents'),
    
    # Annuaire public des agronomes - Exigences: 8.1, 8.2, 8.3, 8.4
    path('agronomists', views.agronomist_directory, name='agronomist-directory'),
    
    # Page de détails publique d'un agronome - Exigence: 8.5
    path('agronomists/<int:agronomist_id>', views.agronomist_public_detail, name='agronomist-public-detail'),
    
    # Validation administrative des agronomes (admin) - Exigences: 7.5, 7.6
    path('agronomists/pending', views.get_pending_agronomists, name='get-pending-agronomists'),
    path('agronomists/<int:agronomist_id>/details', views.get_agronomist_details, name='get-agronomist-details'),
    path('agronomists/<int:agronomist_id>/validate', views.validate_agronomist, name='validate-agronomist'),
    
    # Vérification des exploitations - Exigences: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6
    path('farms/verification-request', views.farm_verification_request, name='farm-verification-request'),
    path('farms/verification-status', views.farm_verification_status, name='farm-verification-status'),
    path('farms/me/premium-features', views.farm_premium_features, name='farm-premium-features'),
    
    # Validation administrative des exploitations (admin) - Exigences: 10.4, 10.5, 10.6
    path('farms/pending', views.get_pending_farms, name='get-pending-farms'),
    path('farms/<int:farm_id>/details', views.get_farm_details, name='get-farm-details'),
    path('farms/<int:farm_id>/verify', views.verify_farm, name='verify-farm'),
]
