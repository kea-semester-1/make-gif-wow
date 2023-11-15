import os
from django.conf import settings
import shlex

from django_rq import get_queue
from rq.job import Job
import subprocess
from . import models
import youtube_dl
from django.http import StreamingHttpResponse
import mimetypes


def mk_gif_ffmpeg(params):
    path = shlex.quote(str(settings.MEDIA_ROOT / f'{params["pk"]}'))
    framerate = params["params"]["framerate"]
    scale = params["params"]["scale"]
    from_format = params["params"]["from_format"]
    to_format = params["params"]["to_format"]
    name = params["params"]["name"]
    single_filename = params["params"].get("single_filename")

    if from_format == "mp4" and to_format == "png":
        path = f"{path}/{single_filename}"
        extract_frames_from_video((path), params["pk"], single_filename)
        return

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
    framerate = params["params"].get("framerate", None)
    scale = params["params"].get("scale", None)
    to_format = params["params"].get("to_format", None)
    new_name = params["params"].get("name", None)
    original_filename = params["params"].get("original_filename", None)
    original_filetype = params["params"].get("original_filetype", None)

    input_file = f"{base_path}/{original_filename}"
    temp_output_file = f"{base_path}/{new_name}_temp.{to_format}"

    # Check if framerate, scale, or to_format is None
    if not all([framerate, scale, to_format]):
        final_output_file = f"{base_path}/{new_name}.{original_filetype}"
        os.rename(input_file, final_output_file)
    else:
        # Construct and execute the FFmpeg command
        final_output_file = f"{base_path}/{new_name}.{to_format}"
        command = f'ffmpeg -y -i "{input_file}" -r {framerate} -vf scale={scale}:-1 "{temp_output_file}"'
        print("Executing command:", command)

        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print("FFmpeg Output:", result.stdout)
        print("FFmpeg Error:", result.stderr)

        # Replace the original file with the temporary output file
        if os.path.exists(temp_output_file):
            if os.path.exists(final_output_file):
                os.remove(final_output_file)
            os.rename(temp_output_file, final_output_file)
        else:
            print(f"Expected output file was not found: {temp_output_file}")


def extract_frames_from_video(video_path, anim_id, name):
    output_path = os.path.join(settings.MEDIA_ROOT, str(anim_id))

    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)

    file_name = os.path.join(output_path, "frame_%04d.png")
    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-r",
        "1",  # Adjust the frame rate as needed
        file_name,
    ]

    # Run the FFmpeg command
    subprocess.run(command, shell=False)

    # list files jut created
    files_created = os.listdir(output_path)
    anim = models.Animation.objects.get(pk=anim_id)
    new_name, new_type = name.split(".")
    anim.type = new_type
    anim.name = new_name
    anim.save()

    for file_name in files_created:
        relative_file_path = os.path.join(str(anim_id), file_name)
        if file_name.endswith(".png"):
            models.Image.objects.create(animation=anim, image=relative_file_path)


def download_and_trim_youtube_video(request, url, start_time, end_time, output_name):
    # Temporary path for the downloaded video
    temp_video_path = os.path.join(settings.TEMP_DIR, "input_file.mp4")

    # Download the video to a temporary location
    ydl_opts = {"format": "best", "outtmpl": temp_video_path, "verbose": True}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Temporary path for the trimmed video
    trimmed_video_path = os.path.join(settings.TEMP_DIR, f"{output_name}.mp4")

    # FFmpeg command to trim the video
    ffmpeg_command = [
        "ffmpeg",
        "-i",
        temp_video_path,
        "-ss",
        start_time,
        "-to",
        end_time,
        "-c",
        "copy",
        trimmed_video_path,
    ]
    subprocess.run(ffmpeg_command, shell=False)

    # Ensure the trimmed file exists
    if not os.path.exists(trimmed_video_path):
        raise FileNotFoundError("Trimmed video file not found.")

    def file_stream():
        with open(trimmed_video_path, "rb") as f:
            yield from f

        # Clean up temporary files
        os.remove(trimmed_video_path)
        os.remove(temp_video_path)

    response = StreamingHttpResponse(file_stream(), content_type="video/mp4")
    response["Content-Disposition"] = f'attachment; filename="{output_name}.mp4"'
    return response
