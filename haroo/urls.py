"""
URL configuration for haroo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import JsonResponse
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)


def root_view(request):
    return JsonResponse({
        'name': 'Haroo API',
        'version': '1.0.0',
        'docs': '/api/docs/',
        'admin': '/admin/',
        'frontend': settings.FRONTEND_URL,
    })


urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints
    path('api/v1/', include('apps.core.urls')),  # Health check & monitoring
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/', include('apps.locations.urls')),
    path('api/v1/', include('apps.documents.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/', include('apps.missions.urls')),
    path('api/v1/institutional/', include('apps.institutional.urls')),
    path('api/v1/compliance/', include('apps.compliance.urls')),
    path('api/v1/ratings/', include('apps.ratings.urls')),
    path('api/v1/', include('apps.notifications.urls')),
    path('api/v1/', include('apps.messaging.urls')),
    path('api/v1/', include('apps.presales.urls')),
    path('api/v1/', include('apps.jobs.urls')),
    path('api/v1/elearning/', include('apps.elearning.urls')),
]

# Ajouter les URLs de debug toolbar uniquement en mode DEBUG
if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
