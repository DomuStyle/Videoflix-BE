"""Unit tests for the logout API endpoint.

This module contains test cases to verify the behavior of the logout view,
including successful logout, missing refresh token, and invalid token scenarios.
"""

from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutTestCase(APITestCase):
    """Test case for the logout endpoint."""
    
    def setUp(self):
        """Set up test data with an active user and refresh token."""
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )
        self.refresh_token = str(RefreshToken.for_user(self.user))  # Generate refresh token
        self.client.cookies['refresh_token'] = self.refresh_token  # Set refresh token cookie

    def test_logout_success(self):
        """Test successful logout with valid refresh token."""
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], 'Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid.')
        self.assertEqual(response.cookies.get('access_token').value, '')  # Verify access token cookie is cleared
        self.assertEqual(response.cookies.get('refresh_token').value, '')  # Verify refresh token cookie is cleared

    def test_logout_no_token(self):
        """Test logout failure when refresh token is missing."""
        self.client.cookies.clear()
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, 400)

    def test_logout_invalid_token(self):
        """Test logout failure with an invalid refresh token."""
        self.client.cookies['refresh_token'] = 'invalid_token'
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, 400)