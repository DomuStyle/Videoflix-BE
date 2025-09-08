"""Unit tests for the HLS segment API endpoint.

This module contains test cases to verify the behavior of the HLS segment view,
including successful segment retrieval, unauthenticated access, and not found scenarios.
"""

from django.conf import settings
from video_content_app.models import Video
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
import os


class HLSSegmentTestCase(APITestCase):
    """Test case for the HLS segment endpoint."""
    
    def setUp(self):
        """Set up test data with a user, JWT token, video, and mock HLS segment file."""
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
        self.segment = '000.ts'
        self.segment_path = os.path.join(settings.MEDIA_ROOT, f'videos/{self.video.id}/{self.resolution}/{self.segment}')
        os.makedirs(os.path.dirname(self.segment_path), exist_ok=True)  # Create directory for mock segment
        with open(self.segment_path, 'wb') as f:
            f.write(b'\x00\x01\x02')  # Write mock binary segment content

    def test_hls_segment_success(self):
        """Test successful retrieval of an HLS segment with valid authentication."""
        url = f'/api/video/{self.video.id}/{self.resolution}/{self.segment}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'video/MP2T')  # Verify correct content type
        content = b''.join(response.streaming_content)  # Aggregate streaming response
        self.assertEqual(content, b'\x00\x01\x02')  # Verify segment content matches mock data

    def test_hls_segment_unauthenticated(self):
        """Test HLS segment access without authentication."""
        self.client.credentials()  # Clear JWT header
        url = f'/api/video/{self.video.id}/{self.resolution}/{self.segment}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_hls_segment_not_found(self):
        """Test HLS segment access for non-existent video, resolution, or segment."""
        url = f'/api/video/9999/{self.resolution}/{self.segment}/'  # Non-existent video ID
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        url = f'/api/video/{self.video.id}/invalid/{self.segment}/'  # Invalid resolution
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        url = f'/api/video/{self.video.id}/{self.resolution}/invalid.ts/'  # Invalid segment
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)