from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import django_rq
from .utils import mk_gif_ffmpeg, edit_media
import os
import shutil


class Animation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    type = models.TextField(max_length=5)

    PROCESSING = "processing"
    COMPLETE = "complete"
    STATUS_CHOICES = [
        (PROCESSING, "Processing"),
        (COMPLETE, "Complete"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PROCESSING)
    job_id = models.CharField(max_length=10)

    def enqueue(self, params):
        job = django_rq.enqueue(
            mk_gif_ffmpeg,
            {
                "pk": self.pk,
                "params": params,
            },
        )
        self.job_id = job.id
        self.save()

    def enqueue_edit(self, params):
        job = django_rq.enqueue(
            edit_media,
            {
                "pk": self.pk,
                "params": params,
            },
        )
        self.job_id = job.id
        self.save()


class Image(models.Model):
    def image_path(self, filename):
        return f"{self.animation.pk}/{filename}"

    animation = models.ForeignKey(
        "Animation",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(upload_to=image_path)

    def delete(self, pk):
        folder_path = os.path.join(settings.MEDIA_ROOT, str(pk))
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            shutil.rmtree(folder_path)
        super().delete()


class Job(models.Model):
    job_id = models.UUIDField(max_length=100)
    file_path = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    file_token = models.UUIDField(max_length=100, default=None, null=True)

    def delete(self, *args, **kwargs):
        if os.path.isfile(self.file_path):
            os.remove(self.file_path)
        super().delete(*args, **kwargs)


class YouTubeVideo(models.Model):
    youtube_url = models.URLField(max_length=1024)
    start_time = models.CharField(max_length=10)  # Format: 'HH:MM:SS'
    end_time = models.CharField(max_length=10)  # Format: 'HH:MM:SS'
    video_name = models.CharField(max_length=100)
