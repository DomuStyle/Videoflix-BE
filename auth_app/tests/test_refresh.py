from rest_framework.test import APITestCase  # imports apitestcase.
from django.contrib.auth.models import User  # imports user model.
from rest_framework_simplejwt.tokens import RefreshToken  # imports refresh token.

class RefreshTestCase(APITestCase):  # defines test case class.
    def setUp(self):  # sets up test data.
        self.user = User.objects.create_user(  # creates user.
            username='test@example.com',  # username = email.
            email='test@example.com',  # email.
            password='testpass123',  # password.
            is_active=True  # active.
        )
        self.refresh_token = str(RefreshToken.for_user(self.user))  # generates valid refresh token.
        self.client.cookies['refresh_token'] = self.refresh_token  # sets refresh token cookie.

    def test_refresh_success(self):  # tests successful refresh.
        response = self.client.post('/api/token/refresh/')  # sends post request.
        self.assertEqual(response.status_code, 200)  # checks 200 status.
        self.assertEqual(response.data['detail'], 'Token refreshed')  # checks detail message.
        self.assertIn('access', response.data)  # checks new access token in response.
        self.assertEqual(response.cookies.get('access_token').value, response.data['access'])  # checks new access token cookie matches response.

    def test_refresh_no_token(self):  # tests missing refresh token.
        self.client.cookies.clear()  # clears cookies.
        response = self.client.post('/api/token/refresh/')  # sends post request.
        self.assertEqual(response.status_code, 400)  # checks 400 status.

    def test_refresh_invalid_token(self):  # tests invalid refresh token.
        self.client.cookies['refresh_token'] = 'invalid_token'  # sets invalid token.
        response = self.client.post('/api/token/refresh/')  # sends post request.
        self.assertEqual(response.status_code, 401)  # checks 401 status.