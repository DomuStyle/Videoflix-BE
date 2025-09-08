"""Unit tests for the video list API endpoint.

This module contains test cases to verify the behavior of the video list view,
including authenticated access, unauthenticated access, caching, and cookie-based JWT authentication.
"""

from video_content_app.models import Video
from django.core.cache import cache
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class VideoListTestCase(APITestCase):
    """Test case for the video list endpoint."""
    
    def setUp(self):
        """Set up test data with a user, JWT token, and sample video."""
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

    def tearDown(self):
        """Clean up test data and cache after each test."""
        self.video.delete()  # Remove created video to prevent data leakage
        cache.clear()  # Clear cache for consistent test state

    def test_video_list_authenticated(self):
        """Test successful video list retrieval with valid authentication."""
        response = self.client.get('/api/video/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # Verify one video is returned
        self.assertEqual(response.data[0]['title'], 'Test Video')  # Verify video title
        self.assertIn('thumbnail_url', response.data[0])  # Verify thumbnail URL is included

    def test_video_list_unauthenticated(self):
        """Test video list access without authentication."""
        self.client.credentials()  # Clear JWT header
        response = self.client.get('/api/video/')
        self.assertEqual(response.status_code, 401)

    def test_video_list_caching(self):
        """Test caching behavior of the video list endpoint."""
        cache_key = 'video_list'
        self.client.get('/api/video/')  # Populate cache with initial request
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)  # Verify cache is set
        self.assertEqual(len(cached_data), 1)  # Verify cached data contains one video

    def test_video_list_cookie_auth(self):
        """Test video list retrieval using cookie-based JWT authentication."""
        self.client.cookies['access_token'] = self.token  # Set JWT in cookie
        response = self.client.get('/api/video/')
        self.assertEqual(response.status_code, 200)