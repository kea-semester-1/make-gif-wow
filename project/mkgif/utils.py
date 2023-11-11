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
    name = params["params"]["name"]
    single_filename = params["params"].get("single_filename")

    if single_filename:
        # Use the single filename passed from the view
        print(single_filename)
        single_filename = single_filename
        input_str = f'-y -i "{path}/{single_filename}"'
    else:
        input_str = (
            f'-framerate {framerate} -pattern_type glob -y -i "{path}/*.{from_format}"'
        )

    command = (
        f'ffmpeg {input_str} -r 15 -vf scale={scale}:-1 "{path}/{name}.{to_format}"'
    )
    print(command)
    os.system(command)


def get_job_status(job_id):
    queue = get_queue()
    job = Job.fetch(job_id, connection=queue.connection)
    return job.get_status()


def mk_gif_ffmpeg_one(params):
    path = shlex.quote(str(settings.MEDIA_ROOT / f'{params["pk"]}'))
    framerate = params["params"]["framerate"]
    scale = params["params"]["scale"]
    from_format = params["params"]["from_format"]
    to_format = params["params"]["to_format"]
    name = params["params"]["name"]
    name_from = params["params"]["name_from"]
    if from_format == "gif" and to_format == "mp4":
        command = f'ffmpeg -i "{path}/{name_from}" -r 15 -vf scale={scale}:-1 "{path}/{name}.{to_format}"'
        print(path, params)
        print(command)
        os.system(command)
