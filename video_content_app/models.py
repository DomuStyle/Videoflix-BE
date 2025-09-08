"""Models for the video content application.

This module defines the Video model for storing video metadata and associated files.
"""

from django.db import models


class Video(models.Model):
    """Model representing a video with metadata and associated files."""
    
    title = models.CharField(max_length=255)  # Video title
    description = models.TextField()  # Video description
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of creation
    thumbnail = models.ImageField(upload_to='thumbnails/')  # Thumbnail image
    category = models.CharField(max_length=100)  # Video category
    original_file = models.FileField(upload_to='videos/original/')  # Original video file

    def __str__(self):
        """Return the string representation of the video.

        Returns:
            str: The title of the video.
        """
        return self.title
