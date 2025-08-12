from django.apps import AppConfig  # imports appconfig.

class VideoContentAppConfig(AppConfig):  # custom app config.
    default_auto_field = 'django.db.models.BigAutoField'  # default pk type.
    name = 'video_content_app'  # app name.

    def ready(self):  # ready method.
        import video_content_app.signals  # imports signals to connect them.
