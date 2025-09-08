"""Configuration for the auth_app Django application.

This module defines the application configuration, including the default auto field
and signal registration.
"""

from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """Configuration class for the auth_app application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'

    def ready(self):
        """Initialize the application and connect signals."""
        import auth_app.signals  # Import signals to register them on app startup