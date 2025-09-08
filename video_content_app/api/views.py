"""API views for video content management and streaming.

This module defines views for listing videos, serving HLS playlists and segments,
and accessing media files, with JWT authentication and caching for performance.
"""

from django.conf import settings
from django.core.cache import cache
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Video
from .serializers import VideoSerializer
from .permissions import IsJWTAuthenticated
import os
import mimetypes


class VideoListView(APIView):
    """Handle listing of all videos with caching."""
    permission_classes = [IsJWTAuthenticated]

    def get(self, request):
        """Retrieve and return a list of all videos, using cache if available.

        Args:
            request: The HTTP request object.

        Returns:
            Response: Serialized video data, either from cache or database.
        """
        cache_key = 'video_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True, context={'request': request})
        data = serializer.data
        cache.set(cache_key, data, timeout=300)  # Cache for 5 minutes
        return Response(data)


class HLSPlaylistView(APIView):
    """Serve HLS playlist files for video streaming."""
    permission_classes = [IsJWTAuthenticated]

    def get(self, request, movie_id, resolution):
        """Serve the HLS playlist file for a specific video and resolution.

        Args:
            request: The HTTP request object.
            movie_id (int): The ID of the video.
            resolution (str): The requested video resolution (e.g., '480p').

        Returns:
            FileResponse: The HLS playlist file.

        Raises:
            Http404: If the video or playlist file is not found.
        """
        try:
            video = Video.objects.get(id=movie_id)
        except Video.DoesNotExist:
            raise Http404

        playlist_path = os.path.join(settings.MEDIA_ROOT, f'videos/{video.id}/{resolution}/index.m3u8')
        if not os.path.exists(playlist_path):
            raise Http404

        return FileResponse(open(playlist_path, 'rb'), content_type='application/vnd.apple.mpegurl')


class HLSSegmentView(APIView):
    """Serve HLS video segment files."""
    permission_classes = [IsJWTAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """Serve a specific HLS video segment for a video and resolution.

        Args:
            request: The HTTP request object.
            movie_id (int): The ID of the video.
            resolution (str): The requested video resolution (e.g., '480p').
            segment (str): The name of the segment file.

        Returns:
            FileResponse: The video segment file.

        Raises:
            Http404: If the video or segment file is not found.
        """
        try:
            video = Video.objects.get(id=movie_id)
        except Video.DoesNotExist:
            raise Http404

        segment_path = os.path.join(settings.MEDIA_ROOT, f'videos/{video.id}/{resolution}/{segment}')
        if not os.path.exists(segment_path):
            raise Http404

        return FileResponse(open(segment_path, 'rb'), content_type='video/MP2T')



class MediaView(APIView):
    """Serve media files such as thumbnails."""
    
    def get(self, request, path):
        """Serve a media file based on the provided path.

        Args:
            request: The HTTP request object.
            path (str): The relative path to the media file (e.g., 'thumbnails/filename.png').

        Returns:
            FileResponse: The requested media file.

        Raises:
            Http404: If the file does not exist or is outside MEDIA_ROOT.
        """
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        # Prevent path traversal and verify file existence
        if not os.path.exists(file_path) or not file_path.startswith(str(settings.MEDIA_ROOT)):
            raise Http404("Media file not found")
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or 'application/octet-stream'
        return FileResponse(open(file_path, 'rb'), content_type=content_type)