from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import django_rq
from .utils import mk_gif_ffmpeg
import os
import shutil


class Animation(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def enqueue(self, params):
        django_rq.enqueue(
            mk_gif_ffmpeg,
            {
                "pk": self.pk,
                "params": params,
            },
        )


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
