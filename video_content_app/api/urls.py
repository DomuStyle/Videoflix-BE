"""URL configuration for the video content API.

This module defines URL patterns for video listing, HLS playlist and segment serving,
and media file access.
"""

from django.urls import path
from .views import VideoListView, HLSPlaylistView, HLSSegmentView, MediaView


urlpatterns = [
    path('video/', VideoListView.as_view(), name='video_list'),  # List all videos
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', HLSPlaylistView.as_view(), name='hls_playlist'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', HLSSegmentView.as_view(), name='hls_segment'),
    path('media/<path:path>', MediaView.as_view(), name='media'),  # Serve media files (e.g., thumbnails)
]