import os
from django.conf import settings


def mk_gif_ffmpeg(params):
    path = settings.MEDIA_ROOT / f'{params["pk"]}'
    command = f'ffmpeg -framerate 60 -pattern_type glob -y -i "{path}/*.png" -r 15 -vf scale=512:-1 {path}/out.gif'
    print(path, params)
    print(command)
    os.system(command)

