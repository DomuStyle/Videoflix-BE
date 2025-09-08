"""URL configuration for the core Django project.

This module defines the root URL patterns, routing requests to the admin interface
and including URL configurations from the auth_app and video_content_app. It also
serves media files in debug mode.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.api.urls')),  # Include authentication API endpoints
    path('api/', include('video_content_app.api.urls')),  # Include video content API endpoints
]

if settings.DEBUG:
    # Serve media files directly during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)