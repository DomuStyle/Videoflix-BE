from django.contrib import admin
from .models import Video  # imports video model.

admin.site.register(Video)  # registers video for admin interface.

