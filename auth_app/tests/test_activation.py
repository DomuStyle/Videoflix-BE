from rest_framework.test import APITestCase  # imports apitestcase for api testing.
from django.contrib.auth.models import User  # imports user model.
from django.utils.http import urlsafe_base64_encode  # imports base64 encode.
from django.utils.encoding import force_bytes  # imports force_bytes.
from django.contrib.auth.tokens import default_token_generator  # imports token generator.

class ActivationTestCase(APITestCase):  # defines test case class.
    def setUp(self):  # sets up test data.
        self.user = User.objects.create_user(  # creates inactive user.
            username='testuser',  # username.
            email='test@example.com',  # email.
            password='testpass123',  # password.
            is_active=False  # inactive for activation.
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))  # encodes user id.
        self.token = default_token_generator.make_token(self.user)  # generates valid token.

    def test_activation_success(self):  # tests successful activation.
        url = f'/api/activate/{self.uidb64}/{self.token}/'  # builds activation url.
        response = self.client.get(url)  # sends get request.
        self.assertEqual(response.status_code, 200)  # checks 200 status.
        self.assertEqual(response.data, {'message': 'Account successfully activated.'})  # checks response.
        self.user.refresh_from_db()  # refreshes user from db.
        self.assertTrue(self.user.is_active)  # checks user is now active.

    def test_activation_invalid_token(self):  # tests invalid token.
        url = f'/api/activate/{self.uidb64}/invalid-token/'  # uses invalid token.
        response = self.client.get(url)  # sends get request.
        self.assertEqual(response.status_code, 400)  # checks 400 status.
        self.user.refresh_from_db()  # refreshes user.
        self.assertFalse(self.user.is_active)  # checks user remains inactive.

    def test_activation_invalid_user(self):  # tests invalid user id.
        invalid_uidb64 = urlsafe_base64_encode(force_bytes(9999))  # non-existent user id.
        url = f'/api/activate/{invalid_uidb64}/{self.token}/'  # builds url.
        response = self.client.get(url)  # sends get request.
        self.assertEqual(response.status_code, 400)  # checks 400 status.