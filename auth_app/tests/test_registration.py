"""Unit tests for the user registration API endpoint.

This module contains test cases to verify the behavior of the registration view,
including successful registration, password mismatch, and existing email scenarios.
"""

from django.contrib.auth.models import User
from django.core import mail
from django.test import override_settings
from rest_framework.test import APITestCase


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    TESTING=True
)
class RegistrationTestCase(APITestCase):
    """Test case for the user registration endpoint."""
    
    def setUp(self):
        """Set up test data by clearing the email outbox."""
        mail.outbox = []  # Clear email outbox for clean test state

    def test_registration_success(self):
        """Test successful user registration with valid data."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirmed_password': 'testpass123'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='test@example.com')
        self.assertFalse(user.is_active)  # Verify user is inactive pending activation
        self.assertEqual(len(mail.outbox), 1)  # Verify one email was sent
        self.assertIn('activate', mail.outbox[0].subject.lower())  # Verify email subject includes 'activate'

    def test_registration_password_mismatch(self):
        """Test registration failure with mismatched passwords."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirmed_password': 'wrong'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, 400)

    def test_registration_existing_email(self):
        """Test registration failure with an existing email."""
        User.objects.create_user(username='existing', email='test@example.com', password='pass', is_active=False)
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirmed_password': 'testpass123'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, 400)