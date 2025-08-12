from django.db import models  # imports models module.

class Video(models.Model):  # defines video model.
    title = models.CharField(max_length=255)  # title field.
    description = models.TextField()  # description field.
    created_at = models.DateTimeField(auto_now_add=True)  # creation timestamp.
    thumbnail = models.ImageField(upload_to='thumbnails/')  # thumbnail image upload.
    category = models.CharField(max_length=100)  # category field.
    original_file = models.FileField(upload_to='videos/original/')  # original video file upload.

    def __str__(self):  # string representation.
        return self.title  # returns title.
