"""Unit tests for the password confirmation API endpoint.

This module contains test cases to verify the behavior of the password confirmation
view, including successful password reset, mismatched passwords, invalid tokens, and
invalid user ID scenarios.
"""

from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.test import APITestCase


class PasswordConfirmTestCase(APITestCase):
    """Test case for the password confirmation endpoint."""
    
    def setUp(self):
        """Set up test data with an active user and password reset token."""
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='oldpass123',
            is_active=True
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))  # Encode user ID for URL
        self.token = PasswordResetTokenGenerator().make_token(self.user)  # Generate password reset token

    def test_password_confirm_success(self):
        """Test successful password reset with valid token and matching passwords."""
        data = {'new_password': 'newpass123', 'confirm_password': 'newpass123'}
        url = f'/api/password_confirm/{self.uidb64}/{self.token}/'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], 'Your Password has been successfully reset.')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))  # Verify new password is set

    def test_password_confirm_mismatch(self):
        """Test password reset failure with mismatched passwords."""
        data = {'new_password': 'newpass123', 'confirm_password': 'wrong'}
        url = f'/api/password_confirm/{self.uidb64}/{self.token}/'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('newpass123'))  # Verify password remains unchanged

    def test_password_confirm_invalid_token(self):
        """Test password reset failure with an invalid token."""
        data = {'new_password': 'newpass123', 'confirm_password': 'newpass123'}
        url = f'/api/password_confirm/{self.uidb64}/invalid/'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('newpass123'))  # Verify password remains unchanged

    def test_password_confirm_invalid_user(self):
        """Test password reset failure with a non-existent user ID."""
        data = {'new_password': 'newpass123', 'confirm_password': 'newpass123'}
        invalid_uidb64 = urlsafe_base64_encode(force_bytes(9999))
        url = f'/api/password_confirm/{invalid_uidb64}/{self.token}/'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)