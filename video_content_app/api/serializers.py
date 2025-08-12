from rest_framework import serializers  # imports serializers.
from ..models import Video  # imports video model.

class VideoSerializer(serializers.ModelSerializer):  # defines video serializer.
    thumbnail_url = serializers.SerializerMethodField()  # custom field for thumbnail url.

    class Meta:  # meta class for config.
        model = Video  # uses video model.
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail_url', 'category']  # fields to serialize.

    def get_thumbnail_url(self, obj):  # gets thumbnail url.
        request = self.context.get('request')  # gets request from context.
        if obj.thumbnail:  # if thumbnail exists.
            return request.build_absolute_uri(obj.thumbnail.url)  # builds full url.
        return None  # returns none if no thumbnail.