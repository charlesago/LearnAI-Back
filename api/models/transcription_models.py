from django.db import models
from django.contrib.auth.models import User


class Transcription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    audio_file = models.FileField(upload_to='transcriptions/audio/')
    content_raw = models.TextField(blank=True, null=True)
    content_cleaned = models.TextField(blank=True, null=True)
    folder = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
