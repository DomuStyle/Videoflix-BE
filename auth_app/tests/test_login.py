"""Unit tests for the login API endpoint.

This module contains test cases to verify the behavior of the login view,
including successful login, invalid credentials, and unauthenticated access.
"""

from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class LoginTestCase(APITestCase):
    """Test case for the login endpoint."""
    
    def setUp(self):
        """Set up test data with an active user for login."""
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )

    def test_login_success(self):
        """Test successful login with valid credentials."""
        data = {'email': 'test@example.com', 'password': 'testpass123'}
        response = self.client.post('/api/login/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], 'Login successful')
        self.assertIn('access_token', response.cookies)  # Verify access token cookie is set
        self.assertIn('refresh_token', response.cookies)  # Verify refresh token cookie is set

    def test_login_invalid_credentials(self):
        """Test login failure with incorrect password."""
        data = {'email': 'test@example.com', 'password': 'wrong'}
        response = self.client.post('/api/login/', data)
        self.assertEqual(response.status_code, 400)

    def test_login_no_auth_required(self):
        """Test login endpoint allows unauthenticated requests."""
        self.client.credentials()  # Clear any authentication headers
        data = {'email': 'test@example.com', 'password': 'testpass123'}
        response = self.client.post('/api/login/', data)
        self.assertEqual(response.status_code, 200)  # Verify no 401 error