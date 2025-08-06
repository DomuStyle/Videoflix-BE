from rest_framework.test import APITestCase  # imports apitestcase for api testing.
from django.contrib.auth.models import User  # imports user model.
from django.core import mail  # imports mail for testing emails.
from django.urls import reverse  # imports reverse for url resolution.
from django.test import override_settings  # imports override_settings.

@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',  # mocks email to outbox.
    TESTING=True  # runs tasks synchronously in tests.
)
class RegistrationTestCase(APITestCase):  # defines test case class.

    def setUp(self):  # add setUp to reset outbox.
        mail.outbox = []  # clears email outbox before each test.

    def test_registration_success(self):  # tests successful registration.
        data = {  # prepares request data.
            'email': 'test@example.com',  # email field.
            'password': 'testpass123',  # password field.
            'confirmed_password': 'testpass123'  # confirmed password.
        }
        response = self.client.post('/api/register/', data)  # posts to endpoint.
        self.assertEqual(response.status_code, 201)  # checks 201 status.
        user = User.objects.get(email='test@example.com')  # gets created user.
        self.assertFalse(user.is_active)  # checks user is inactive.
        self.assertEqual(len(mail.outbox), 1)  # checks one email sent.
        self.assertIn('activate', mail.outbox[0].subject.lower())  # checks email subject (fixed!).
        # Changed 'activation' to 'activate' to match 'Activate Your Account'.

    def test_registration_password_mismatch(self):  # tests password mismatch.
        data = {  # data with mismatch.
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirmed_password': 'wrong'
        }
        response = self.client.post('/api/register/', data)  # posts.
        self.assertEqual(response.status_code, 400)  # checks 400.

    def test_registration_existing_email(self):  # tests existing email.
        User.objects.create_user(username='existing', email='test@example.com', password='pass', is_active=False)  # creates user, set is_active=False.
        data = {  # data with same email.
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirmed_password': 'testpass123'
        }
        response = self.client.post('/api/register/', data)  # posts.
        self.assertEqual(response.status_code, 400)  # checks 400.