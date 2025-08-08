from rest_framework.test import APITestCase  # imports apitestcase for api testing.
from django.contrib.auth.models import User  # imports user model.
from django.core import mail  # imports mail for testing emails.
from django.test import override_settings  # imports override_settings.

@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',  # mocks email to outbox.
    TESTING=True  # runs RQ tasks synchronously in tests.
)
class PasswordResetTestCase(APITestCase):  # defines test case class.
    def setUp(self):  # sets up test data.
        mail.outbox = []  # clears email outbox before each test.
        self.user = User.objects.create_user(  # creates user for existing email test.
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            is_active=True
        )

    def test_password_reset_success_existing_email(self):  # tests success for existing email.
        data = {'email': 'test@example.com'}  # request data.
        response = self.client.post('/api/password_reset/', data)  # sends post request.
        self.assertEqual(response.status_code, 200)  # checks 200 status.
        self.assertEqual(response.data['detail'], 'An email has been sent to reset your password.')  # checks response detail.
        self.assertEqual(len(mail.outbox), 1)  # checks one email sent.
        self.assertIn('reset', mail.outbox[0].subject.lower())  # checks email subject contains 'reset'.
        self.assertIn('http://your-frontend-ip/pages/auth/reset.html', mail.outbox[0].body)  # checks reset link in body (adapt if frontend URL changes).

    def test_password_reset_success_non_existing_email(self):  # tests success for non-existent email.
        data = {'email': 'nonexistent@example.com'}  # request data.
        response = self.client.post('/api/password_reset/', data)  # sends post request.
        self.assertEqual(response.status_code, 200)  # checks 200 status.
        self.assertEqual(response.data['detail'], 'An email has been sent to reset your password.')  # checks response detail.
        self.assertEqual(len(mail.outbox), 1)  # checks one email sent (per doc, always sends).

    def test_password_reset_invalid_email_format(self):  # tests invalid email format.
        data = {'email': 'invalid_email'}  # invalid email data.
        response = self.client.post('/api/password_reset/', data)  # sends post request.
        self.assertEqual(response.status_code, 400)  # checks 400 status.
        self.assertEqual(len(mail.outbox), 0)  # checks no email sent.