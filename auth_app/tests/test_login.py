
from rest_framework.test import APITestCase  # imports apitestcase.
from django.contrib.auth.models import User  # imports user model.

class LoginTestCase(APITestCase):  # defines test case class.
    def setUp(self):  # sets up test data.
        self.user = User.objects.create_user(  # creates active user.
            username='test@example.com',  # username matches email (fix for authentication).
            email='test@example.com',  # email.
            password='testpass123',  # password.
            is_active=True  # active for login.
        )

    def test_login_success(self):  # tests successful login.
        data = {'email': 'test@example.com', 'password': 'testpass123'}  # login data.
        response = self.client.post('/api/login/', data)  # sends post request.
        self.assertEqual(response.status_code, 200)  # checks 200 status.
        self.assertEqual(response.data['detail'], 'Login successful')  # checks detail message.
        self.assertIn('access_token', response.cookies)  # checks access token cookie.
        self.assertIn('refresh_token', response.cookies)  # checks refresh token cookie.

    def test_login_invalid_credentials(self):  # tests invalid credentials.
        data = {'email': 'test@example.com', 'password': 'wrong'}  # wrong password.
        response = self.client.post('/api/login/', data)  # sends post request.
        self.assertEqual(response.status_code, 400)  # checks 400 status.