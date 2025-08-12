from rest_framework.views import APIView  # imports apiview.
from rest_framework.response import Response  # imports response.
from rest_framework import status  # imports status codes.
from ..models import Video  # imports video model.
from .serializers import VideoSerializer  # imports serializer.
from .permissions import IsJWTAuthenticated  # imports permission.
from django.core.cache import cache  # imports cache.

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