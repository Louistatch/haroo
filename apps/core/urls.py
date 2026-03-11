from django.urls import path
from . import views
from . import views_storage
from . import views_admin

urlpatterns = [
    path('ping/', views.ping, name='ping'),  # Lightweight healthcheck (no DB)
    path('auth-debug/', views.auth_debug, name='auth-debug'),  # Debug auth token
    path('health/', views.health_check, name='health-check'),
    path('health/detailed/', views.health_check_detailed, name='health-check-detailed'),
    # AI Assistant
    path('ai/chat/', views.ai_chat, name='ai-chat'),
    path('ai/chat/reset/', views.ai_chat_reset, name='ai-chat-reset'),
    # Supabase Storage
    path('storage/upload/', views_storage.upload_file, name='storage-upload'),
    path('storage/signed-url/', views_storage.get_signed_url, name='storage-signed-url'),
    path('storage/delete/', views_storage.delete_file, name='storage-delete'),
    # Admin Dashboard
    path('admin/dashboard/', views_admin.admin_dashboard, name='admin-dashboard'),
    path('admin/users/', views_admin.admin_users, name='admin-users'),
    path('admin/users/<int:user_id>/suspend/', views_admin.admin_suspend_user, name='admin-suspend-user'),
    path('admin/users/<int:user_id>/activate/', views_admin.admin_activate_user, name='admin-activate-user'),
]
