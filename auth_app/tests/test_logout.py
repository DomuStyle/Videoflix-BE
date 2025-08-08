from rest_framework.test import APITestCase  # imports apitestcase.
from django.contrib.auth.models import User  # imports user model.
from rest_framework_simplejwt.tokens import RefreshToken  # imports refresh token.

class LogoutTestCase(APITestCase):  # defines test case class.
    def setUp(self):  # sets up test data.
        self.user = User.objects.create_user(  # creates user.
            username='test@example.com',  # username = email.
            email='test@example.com',  # email.
            password='testpass123',  # password.
            is_active=True  # active.
        )
        self.refresh_token = str(RefreshToken.for_user(self.user))  # generates refresh token.
        self.client.cookies['refresh_token'] = self.refresh_token  # sets refresh token cookie.

    def test_logout_success(self):  # tests successful logout.
        response = self.client.post('/api/logout/')  # sends post request.
        self.assertEqual(response.status_code, 200)  # checks 200 status.
        self.assertEqual(response.data['detail'], 'Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid.')  # checks response detail.
        self.assertEqual(response.cookies.get('access_token').value, '')  # checks access token deleted (empty value).
        self.assertEqual(response.cookies.get('refresh_token').value, '')  # checks refresh token deleted (empty value).

    def test_logout_no_token(self):  # tests missing refresh token.
        self.client.cookies.clear()  # clears cookies.
        response = self.client.post('/api/logout/')  # sends post request.
        self.assertEqual(response.status_code, 400)  # checks 400 status.

    def test_logout_invalid_token(self):  # tests invalid refresh token.
        self.client.cookies['refresh_token'] = 'invalid_token'  # sets invalid token.
        response = self.client.post('/api/logout/')  # sends post request.
        self.assertEqual(response.status_code, 400)  # checks 400 status.