import os
from django.conf import settings
import shlex

from django_rq import get_queue
from rq.job import Job


def mk_gif_ffmpeg(params):
    path = shlex.quote(str(settings.MEDIA_ROOT / f'{params["pk"]}'))
    framerate = params["params"]["framerate"]
    scale = params["params"]["scale"]
    from_format = params["params"]["from_format"]
    to_format = params["params"]["to_format"]
    command = f'ffmpeg -framerate {framerate} -pattern_type glob -y -i "{path}/*.{from_format}" -r 15 -vf scale={scale}:-1 {path}/out.{to_format}'
    print(path, params)
    print(command)
    os.system(command)


def get_job_status(job_id):
    queue = get_queue()  
    job = Job.fetch(job_id, connection=queue.connection)
    return job.get_status()
