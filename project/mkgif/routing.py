from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/status/(?P<pk>\d+)/$", consumers.StatusConsumer.as_asgi()),
    re_path(
        r"ws/status/mp3/(?P<job_id>[^/]+)/$", consumers.MP3ConversionConsumer.as_asgi()
    ),
]
