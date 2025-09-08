"""Unit tests for the HLS playlist API endpoint.

This module contains test cases to verify the behavior of the HLS playlist view,
including successful playlist retrieval, unauthenticated access, and not found scenarios.
"""

from django.conf import settings
from video_content_app.models import Video
from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
import os


class HLSPlaylistTestCase(APITestCase):
    """Test case for the HLS playlist endpoint."""
    
    def setUp(self):
        """Set up test data with a user, JWT token, video, and mock HLS playlist file."""
        self.user = User.objects.create_user(username='test@example.com', password='testpass123')
        self.token = str(RefreshToken.for_user(self.user).access_token)  # Generate JWT access token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')  # Set JWT header for authentication

        self.video = Video.objects.create(
            title='Test Video',
            description='Test desc',
            thumbnail='thumbnails/test.jpg',
            category='Drama',
            original_file='videos/original/test.mp4'
        )
        self.resolution = '480p'
        self.playlist_path = os.path.join(settings.MEDIA_ROOT, f'videos/{self.video.id}/{self.resolution}/index.m3u8')
        os.makedirs(os.path.dirname(self.playlist_path), exist_ok=True)  # Create directory for mock playlist
        with open(self.playlist_path, 'w') as f:
            f.write('#EXTM3U\n#EXT-X-VERSION:3\n')  # Write mock HLS playlist content

    def test_hls_playlist_success(self):
        """Test successful retrieval of an HLS playlist with valid authentication."""
        url = f'/api/video/{self.video.id}/{self.resolution}/index.m3u8'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.apple.mpegurl')  # Verify correct content type
        content = b''.join(response.streaming_content).decode()  # Decode streaming response
        self.assertIn('#EXTM3U', content)  # Verify HLS playlist content

    def test_hls_playlist_unauthenticated(self):
        """Test HLS playlist access without authentication."""
        self.client.credentials()  # Clear JWT header
        url = f'/api/video/{self.video.id}/{self.resolution}/index.m3u8'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_hls_playlist_not_found(self):
        """Test HLS playlist access for non-existent video or invalid resolution."""
        url = f'/api/video/9999/{self.resolution}/index.m3u8'  # Non-existent video ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        url = f'/api/video/{self.video.id}/invalid/index.m3u8'  # Invalid resolution
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)