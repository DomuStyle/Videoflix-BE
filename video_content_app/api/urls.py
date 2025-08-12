from django.urls import path  # imports path.
from .views import VideoListView  # imports view.

urlpatterns = [  # url patterns list.
    path('video/', VideoListView.as_view(), name='video_list'),  # video list url.
]