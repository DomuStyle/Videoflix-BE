"""Unit tests for the password reset API endpoint.

This module contains test cases to verify the behavior of the password reset view,
including successful resets for existing and non-existing emails, and invalid email
format handling.
"""

from django.contrib.auth.models import User
from django.core import mail
from django.test import override_settings
from rest_framework.test import APITestCase


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    TESTING=True
)
class PasswordResetTestCase(APITestCase):
    """Test case for the password reset endpoint."""
    
    def setUp(self):
        """Set up test data with an active user and clear email outbox."""
        mail.outbox = []  # Clear email outbox for clean test state
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )

    def test_password_reset_success_existing_email(self):
        """Test successful password reset request for an existing email."""
        data = {'email': 'test@example.com'}
        response = self.client.post('/api/password_reset/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], 'An email has been sent to reset your password.')
        self.assertEqual(len(mail.outbox), 1)  # Verify one email was sent
        self.assertIn('reset', mail.outbox[0].subject.lower())  # Verify email subject includes 'reset'
        self.assertIn('http://localhost:5500/pages/auth/confirm_password.html', mail.outbox[0].body)  # Verify reset link in email body

    def test_password_reset_success_non_existing_email(self):
        """Test password reset request for a non-existent email."""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post('/api/password_reset/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], 'An email has been sent to reset your password.')
        self.assertEqual(len(mail.outbox), 1)  # Verify one email was sent

    def test_password_reset_invalid_email_format(self):
        """Test password reset failure with an invalid email format."""
        data = {'email': 'invalid_email'}
        response = self.client.post('/api/password_reset/', data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)  # Verify no email was sent