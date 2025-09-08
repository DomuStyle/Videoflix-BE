"""Serializers for the video content API.

This module defines serializers for the Video model, including custom handling
for generating thumbnail URLs.
"""

from rest_framework import serializers
from ..models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for the Video model, including a custom thumbnail URL field."""
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        """Configuration for the VideoSerializer."""
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail_url', 'category']

    def get_thumbnail_url(self, obj):
        """Generate the absolute URL for the video's thumbnail.

        Args:
            obj: The Video instance being serialized.

        Returns:
            str or None: The absolute URL to the thumbnail, or None if no thumbnail exists.
        """
        request = self.context.get('request')
        if obj.thumbnail:
            # Remove leading slash from thumbnail path for consistent URL building
            relative_path = str(obj.thumbnail).lstrip('/')
            # Construct URL using custom /api/media/ route
            return request.build_absolute_uri(f'/api/media/{relative_path}')
        return None