from django.urls import path  # imports path.
from .views import VideoListView, HLSPlaylistView # imports view.

urlpatterns = [  # url patterns list.
    path('video/', VideoListView.as_view(), name='video_list'),  # video list url.
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', HLSPlaylistView.as_view(), name='hls_playlist'),  # hls playlist url.
]