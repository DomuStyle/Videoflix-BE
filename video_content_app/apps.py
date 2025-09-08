"""Configuration for the video_content_app Django application.

This module defines the application configuration, including the default auto field
and signal registration for video content management.
"""

from django.apps import AppConfig
    

class VideoContentAppConfig(AppConfig): 
    """Configuration class for the video_content_app application."""
    default_auto_field = 'django.db.models.BigAutoField'  
    name = 'video_content_app'  

    def ready(self): 
        """Initialize the application and connect signals."""
        import video_content_app.signals 