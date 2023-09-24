import os
from django.conf import settings
import shlex


def mk_gif_ffmpeg(params):
    path = shlex.quote(str(settings.MEDIA_ROOT / f'{params["pk"]}'))
    framerate = params["params"]["framerate"]
    scale = params["params"]["scale"]
    command = f'ffmpeg -framerate {framerate} -pattern_type glob -y -i "{path}/*.png" -r 15 -vf scale={scale}:-1 {path}/out.gif'
    print(path, params)
    print(command)
    os.system(command)
