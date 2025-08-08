from rest_framework.test import APITestCase  # imports apitestcase for api testing.
from django.contrib.auth.models import User  # imports user model.
from django.utils.http import urlsafe_base64_encode  # imports base64 encode.
from django.utils.encoding import force_bytes  # imports force_bytes.
from django.contrib.auth.tokens import PasswordResetTokenGenerator  # imports token generator.

class PasswordConfirmTestCase(APITestCase):  # defines test case class.
    def setUp(self):  # sets up test data.
        self.user = User.objects.create_user(  # creates user.
            username='test@example.com',  # username = email.
            email='test@example.com',  # email.
            password='oldpass123',  # old password.
            is_active=True  # active.
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))  # encodes user id.
        self.token = PasswordResetTokenGenerator().make_token(self.user)  # generates valid token.

    def test_password_confirm_success(self):  # tests successful confirm.
        data = {'new_password': 'newpass123', 'confirm_password': 'newpass123'}  # matching passwords.
        url = f'/api/password_confirm/{self.uidb64}/{self.token}/'  # builds url.
        response = self.client.post(url, data)  # sends post request.
        self.assertEqual(response.status_code, 200)  # checks 200 status.
        self.assertEqual(response.data['detail'], 'Your Password has been successfully reset.')  # checks response detail.
        self.user.refresh_from_db()  # refreshes user.
        self.assertTrue(self.user.check_password('newpass123'))  # checks new password set.

    def test_password_confirm_mismatch(self):  # tests mismatched passwords.
        data = {'new_password': 'newpass123', 'confirm_password': 'wrong'}  # mismatch.
        url = f'/api/password_confirm/{self.uidb64}/{self.token}/'  # builds url.
        response = self.client.post(url, data)  # sends post request.
        self.assertEqual(response.status_code, 400)  # checks 400 status.
        self.user.refresh_from_db()  # refreshes user.
        self.assertFalse(self.user.check_password('newpass123'))  # checks password unchanged.

    def test_password_confirm_invalid_token(self):  # tests invalid token.
        data = {'new_password': 'newpass123', 'confirm_password': 'newpass123'}  # matching passwords.
        url = f'/api/password_confirm/{self.uidb64}/invalid/'  # invalid token.
        response = self.client.post(url, data)  # sends post request.
        self.assertEqual(response.status_code, 400)  # checks 400 status.
        self.user.refresh_from_db()  # refreshes user.
        self.assertFalse(self.user.check_password('newpass123'))  # checks password unchanged.

    def test_password_confirm_invalid_user(self):  # tests invalid user.
        data = {'new_password': 'newpass123', 'confirm_password': 'newpass123'}  # matching passwords.
        invalid_uidb64 = urlsafe_base64_encode(force_bytes(9999))  # non-existent user id.
        url = f'/api/password_confirm/{invalid_uidb64}/{self.token}/'  # builds url.
        response = self.client.post(url, data)  # sends post request.
        self.assertEqual(response.status_code, 400)  # checks 400 status.