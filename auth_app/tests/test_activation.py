"""Unit tests for the account activation API endpoint.

This module contains test cases to verify the behavior of the activation view,
including successful activation, invalid token handling, and invalid user ID scenarios.
"""

from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APITestCase


class ActivationTestCase(APITestCase):
    """Test case for the account activation endpoint."""
    
    def setUp(self):
        """Set up test data with an inactive user and activation token."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=False
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))  # Encode user ID for URL
        self.token = default_token_generator.make_token(self.user)  # Generate activation token

    def test_activation_success(self):
        """Test successful account activation with valid UID and token."""
        url = f'/api/activate/{self.uidb64}/{self.token}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'message': 'Account successfully activated.'})
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_activation_invalid_token(self):
        """Test activation failure with an invalid token."""
        url = f'/api/activate/{self.uidb64}/invalid-token/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_activation_invalid_user(self):
        """Test activation failure with a non-existent user ID."""
        invalid_uidb64 = urlsafe_base64_encode(force_bytes(9999))
        url = f'/api/activate/{invalid_uidb64}/{self.token}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)