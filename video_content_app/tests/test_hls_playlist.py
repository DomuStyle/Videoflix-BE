from rest_framework.test import APITestCase  # imports apitestcase for api testing.
from video_content_app.models import Video  # imports video model.
from django.contrib.auth.models import User  # imports user for jwt.
from rest_framework_simplejwt.tokens import RefreshToken  # imports refresh token for auth.
from django.conf import settings  # imports settings for media root.
import os  # imports os for file paths.
from django.test import override_settings  # imports override_settings for testing.

class HLSPlaylistTestCase(APITestCase):  # defines test case class.
    def setUp(self):  # sets up test data.
        self.user = User.objects.create_user(username='test@example.com', password='testpass123')  # creates user for jwt.
        self.token = str(RefreshToken.for_user(self.user).access_token)  # generates access token.
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')  # sets jwt header.

        self.video = Video.objects.create(  # creates video.
            title='Test Video',  # title.
            description='Test desc',  # description.
            thumbnail='thumbnails/test.jpg',  # thumbnail.
            category='Drama',  # category.
            original_file='videos/original/test.mp4'  # original file.
        )
        self.resolution = '480p'  # test resolution.
        self.playlist_path = os.path.join(settings.MEDIA_ROOT, f'videos/{self.video.id}/{self.resolution}/index.m3u8')  # assumed path.
        os.makedirs(os.path.dirname(self.playlist_path), exist_ok=True)  # creates directory.
        with open(self.playlist_path, 'w') as f:  # creates mock m3u8 file.
            f.write('#EXTM3U\n#EXT-X-VERSION:3\n')  # mock content.

    def test_hls_playlist_success(self):  # tests successful playlist.
        url = f'/api/video/{self.video.id}/{self.resolution}/index.m3u8'  # builds url.
        response = self.client.get(url)  # sends get request.
        self.assertEqual(response.status_code, 200)  # checks 200 status.
        self.assertEqual(response['Content-Type'], 'application/vnd.apple.mpegurl')  # checks content type.
        content = b''.join(response.streaming_content).decode()  # consumes streaming_content and decodes to string.
        self.assertIn('#EXTM3U', content)  # checks mock content in decoded string.

    def test_hls_playlist_unauthenticated(self):  # tests unauthenticated.
        self.client.credentials()  # clears jwt header.
        url = f'/api/video/{self.video.id}/{self.resolution}/index.m3u8'  # builds url.
        response = self.client.get(url)  # sends get request.
        self.assertEqual(response.status_code, 401)  # checks 401 status.

    def test_hls_playlist_not_found(self):  # tests not found.
        url = f'/api/video/9999/{self.resolution}/index.m3u8'  # non-existent id.
        response = self.client.get(url)  # sends get request.
        self.assertEqual(response.status_code, 404)  # checks 404 status.

        url = f'/api/video/{self.video.id}/invalid/index.m3u8'  # invalid resolution.
        response = self.client.get(url)  # sends get request.
        self.assertEqual(response.status_code, 404)  # checks 404 status.