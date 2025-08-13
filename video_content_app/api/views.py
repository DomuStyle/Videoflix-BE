from django.conf import settings
from rest_framework.views import APIView  # imports apiview.
from rest_framework.response import Response  # imports response.
from rest_framework import status  # imports status codes.
from ..models import Video  # imports video model.
from .serializers import VideoSerializer  # imports serializer.
from .permissions import IsJWTAuthenticated  # imports permission.
from django.core.cache import cache  # imports cache.
from django.http import FileResponse, Http404  # imports file response and 404.
import os

class VideoListView(APIView):  # defines video list view.
    permission_classes = [IsJWTAuthenticated]  # requires jwt authentication.

    def get(self, request):  # handles get request.
        cache_key = 'video_list'  # cache key for list.
        cached_data = cache.get(cache_key)  # gets cached data.
        if cached_data:  # if cached.
            return Response(cached_data)  # returns cached response.
        videos = Video.objects.all()  # queries all videos.
        serializer = VideoSerializer(videos, many=True, context={'request': request})  # serializes with request context for urls.
        data = serializer.data  # gets serialized data.
        cache.set(cache_key, data, timeout=300)  # caches for 5 minutes.
        return Response(data)  # returns data.
    
class HLSPlaylistView(APIView):  # defines hls playlist view.
    permission_classes = [IsJWTAuthenticated]  # requires jwt authentication.

    def get(self, request, movie_id, resolution):  # handles get request with params.
        try:
            video = Video.objects.get(id=movie_id)  # gets video by id.
        except Video.DoesNotExist:
            raise Http404  # raises 404 if not found.

        playlist_path = os.path.join(settings.MEDIA_ROOT, f'videos/{video.id}/{resolution}/index.m3u8')  # builds path.
        if not os.path.exists(playlist_path):  # checks if file exists.
            raise Http404  # raises 404 if not.

        return FileResponse(open(playlist_path, 'rb'), content_type='application/vnd.apple.mpegurl')  # serves file.  