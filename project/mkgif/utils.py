import os
from django.conf import settings
import shlex

from django_rq import get_queue
from rq.job import Job
import subprocess


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


def edit_media(params):
    base_path = settings.MEDIA_ROOT / str(params["pk"])
    framerate = params["params"]["framerate"]
    scale = params["params"]["scale"]
    to_format = params["params"]["to_format"]
    new_name = params["params"]["name"]
    original_filename = params["params"]["original_filename"]

    input_file = f"{base_path}/{original_filename}"
    temp_output_file = f"{base_path}/{new_name}_temp.{to_format}"

    # Construct the FFmpeg command for editing the media file
    command = f'ffmpeg -y -i "{input_file}" -r {framerate} -vf scale={scale}:-1 "{temp_output_file}"'
    print("Executing command:", command)

    # Execute the command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print("FFmpeg Output:", result.stdout)
    print("FFmpeg Error:", result.stderr)

    # Replace the original file with the temporary output file
    if os.path.exists(temp_output_file):
        final_output_file = f"{base_path}/{new_name}.{to_format}"
        if os.path.exists(final_output_file):
            os.remove(final_output_file)
        os.rename(temp_output_file, final_output_file)
    else:
        print(f"Expected output file was not found: {temp_output_file}")
