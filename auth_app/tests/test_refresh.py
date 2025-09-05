"""Unit tests for the token refresh API endpoint.

This module contains test cases to verify the behavior of the token refresh view,
including successful token refresh, missing refresh token, and invalid token scenarios.
"""

from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class RefreshTestCase(APITestCase):
    """Test case for the token refresh endpoint."""
    
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

    def test_refresh_success(self):
        """Test successful token refresh with a valid refresh token."""
        response = self.client.post('/api/token/refresh/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], 'Token refreshed')
        self.assertIn('access', response.data)  # Verify new access token in response
        self.assertEqual(response.cookies.get('access_token').value, response.data['access'])  # Verify access token cookie matches response

    def test_refresh_no_token(self):
        """Test token refresh failure when refresh token is missing."""
        self.client.cookies.clear()
        response = self.client.post('/api/token/refresh/')
        self.assertEqual(response.status_code, 400)

    def test_refresh_invalid_token(self):
        """Test token refresh failure with an invalid refresh token."""
        self.client.cookies['refresh_token'] = 'invalid_token'
        response = self.client.post('/api/token/refresh/')
        self.assertEqual(response.status_code, 401)