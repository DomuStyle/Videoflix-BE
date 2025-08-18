from rest_framework.test import APITestCase  # imports apitestcase for api testing.
from video_content_app.models import Video  # imports video model.
from django.contrib.auth.models import User  # imports user for jwt.
from rest_framework_simplejwt.tokens import RefreshToken  # imports refresh token for auth.
from django.conf import settings  # imports settings for media root.
import os  # imports os for file paths.

class HLSSegmentTestCase(APITestCase):  # defines test case class.
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
        self.segment = '000.ts'  # test segment name.
        self.segment_path = os.path.join(settings.MEDIA_ROOT, f'videos/{self.video.id}/{self.resolution}/{self.segment}')  # assumed path.
        os.makedirs(os.path.dirname(self.segment_path), exist_ok=True)  # creates directory.
        with open(self.segment_path, 'wb') as f:  # creates mock .ts file (binary).
            f.write(b'\x00\x01\x02')  # mock binary content.

    def test_hls_segment_success(self):  # tests successful segment.
        url = f'/api/video/{self.video.id}/{self.resolution}/{self.segment}/'  # builds url.
        response = self.client.get(url)  # sends get request.
        self.assertEqual(response.status_code, 200)  # checks 200 status.
        self.assertEqual(response['Content-Type'], 'video/MP2T')  # checks content type.
        content = b''.join(response.streaming_content)  # consumes streaming_content as bytes.
        self.assertEqual(content, b'\x00\x01\x02')  # checks mock binary content.

    def test_hls_segment_unauthenticated(self):  # tests unauthenticated.
        self.client.credentials()  # clears jwt header.
        url = f'/api/video/{self.video.id}/{self.resolution}/{self.segment}/'  # builds url.
        response = self.client.get(url)  # sends get request.
        self.assertEqual(response.status_code, 401)  # checks 401 status.

    def test_hls_segment_not_found(self):  # tests not found.
        url = f'/api/video/9999/{self.resolution}/{self.segment}/'  # non-existent id.
        response = self.client.get(url)  # sends get request.
        self.assertEqual(response.status_code, 404)  # checks 404 status.

        url = f'/api/video/{self.video.id}/invalid/{self.segment}/'  # invalid resolution.
        response = self.client.get(url)  # sends get request.
        self.assertEqual(response.status_code, 404)  # checks 404 status.

        url = f'/api/video/{self.video.id}/{self.resolution}/invalid.ts/'  # invalid segment.
        response = self.client.get(url)  # sends get request.
        self.assertEqual(response.status_code, 404)  # checks 404 status.