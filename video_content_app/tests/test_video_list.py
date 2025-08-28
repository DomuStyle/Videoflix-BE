from rest_framework.test import APITestCase  # imports apitestcase for api testing.
from video_content_app.models import Video  # imports video model.
from django.core.cache import cache  # imports cache for testing.
from rest_framework_simplejwt.tokens import RefreshToken  # imports refresh token for auth.
from django.contrib.auth.models import User  # imports user for jwt.

class VideoListTestCase(APITestCase):  # defines test case class.
    def setUp(self):  # sets up test data.
        self.user = User.objects.create_user(username='test@example.com', password='testpass123')  # creates user for jwt.
        self.token = str(RefreshToken.for_user(self.user).access_token)  # generates access token.
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')  # sets jwt header for authenticated requests.
        self.video = Video.objects.create(  # creates sample video.
            title='Test Video',  # title.
            description='Test desc',  # description.
            thumbnail='thumbnails/test.jpg',  # thumbnail.
            category='Drama',  # category.
            original_file='videos/original/test.mp4'  # original file.
        )

    def tearDown(self):  # cleans up after each test.
        self.video.delete()  # deletes the created video to prevent leakage.
        cache.clear()  # clears cache to reset for caching test.

    def test_video_list_authenticated(self):  # tests authenticated list.
        response = self.client.get('/api/video/')  # sends get request.
        self.assertEqual(response.status_code, 200)  # checks 200 status.
        self.assertEqual(len(response.data), 1)  # checks one video returned.
        self.assertEqual(response.data[0]['title'], 'Test Video')  # checks title.
        self.assertIn('thumbnail_url', response.data[0])  # checks thumbnail url present.

    def test_video_list_unauthenticated(self):  # tests unauthenticated.
        self.client.credentials()  # clears jwt header.
        response = self.client.get('/api/video/')  # sends get request.
        self.assertEqual(response.status_code, 401)  # checks 401 status.

    def test_video_list_caching(self):  # tests caching.
        cache_key = 'video_list'  # cache key used in view.
        self.client.get('/api/video/')  # first call, populates cache.
        cached_data = cache.get(cache_key)  # gets from cache.
        self.assertIsNotNone(cached_data)  # checks cache set.
        self.assertEqual(len(cached_data), 1)  # checks cached data length.

    def test_video_list_cookie_auth(self):  # tests cookie jwt.
        self.client.cookies['access_token'] = self.token  # sets cookie instead of header.
        response = self.client.get('/api/video/')
        self.assertEqual(response.status_code, 200)  # checks 200 with cookie.