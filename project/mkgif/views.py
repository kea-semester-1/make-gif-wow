from .models import Animation, Image, Job
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib.auth.decorators import login_required
from mkgif.forms import AnimationForm, YouTubeDownloadForm, MusicDownloadForm
from django.http import HttpResponseRedirect, FileResponse
from mkgif.utils import get_job_status
from django.http import JsonResponse
from django.core.paginator import Paginator
import django_rq
import os

from .utils import download_and_trim_youtube_video, convert_mp4_to_mp3


def index(request):
    return HttpResponseRedirect(reverse("mkgif:animation"))


@login_required
def animation_list(request):
    """View for animation list and creation."""

    animation_form = None

    if request.method == "POST":
        animation_form = AnimationForm(request.POST)
        if animation_form.is_valid():
            anim = animation_form.save(commit=False)
            anim.user = request.user
            anim.type = animation_form.cleaned_data["select_type_to"]
            anim.save()

            images = request.FILES.getlist("imgs")
            for img in images:
                Image.objects.create(animation=anim, image=img)

            params = {
                "framerate": animation_form.cleaned_data["framerate"],
                "scale": animation_form.cleaned_data["scale"],
                "from_format": animation_form.cleaned_data["select_type_from"],
                "to_format": animation_form.cleaned_data["select_type_to"],
                "name": animation_form.cleaned_data["name"],
                "amount_of_files": len(images),
            }

            # If only one image, add the filename to the parameters
            if len(images) == 1:
                params["single_filename"] = images[0].name

            anim.enqueue(params)
            animation_form = None

    if not animation_form:
        animation_form = AnimationForm()

    anims = Animation.objects.filter(user=request.user).order_by("-pk")
    paginator = Paginator(anims, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"animation_form": animation_form, "page_obj": page_obj}
    return render(request, "mkgif/index.html", context)


@login_required
def animation_details(request, pk):
    """View for detailes on an a animation, by pk."""

    anim = get_object_or_404(Animation, pk=pk)

    if request.method == "POST":
        # TODO: find a better way to do this.
        name = request.POST.get("name", None)
        framerate = request.POST["framerate"]
        scale = request.POST["scale"]
        from_format = request.POST["select_type_from"]
        to_format = request.POST["select_type_to"]

        params = {
            "name": name if name else anim.name,
            "original_filename": f"{anim.name}.{anim.type}",
            "original_filetype": f"{anim.type}",
        }

        if all([framerate, scale, from_format, to_format]):
            params.update(
                {
                    "framerate": framerate,
                    "scale": scale,
                    "from_format": from_format,
                    "to_format": to_format,
                }
            )
            anim.type = to_format
        anim.enqueue_edit(params=params)

        anim.name = name if name else anim.name
        anim.save()

        return redirect("mkgif:index")

    if request.method == "DELETE":
        # Delete the associated Image objects and their physical files
        for image in anim.image_set.all():
            image.delete(anim.pk)

        # Delete the Animation object
        anim.delete()

        return redirect("mkgif:index")

    images = Image.objects.filter(animation=pk)
    paginator = Paginator(images, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"anim": anim, "page_obj_detail": page_obj}
    return render(request, "mkgif/details.html", context)


@login_required
def status(request, pk):
    """Status view, that check how far a job is."""
    animation = Animation.objects.get(pk=pk)
    status = get_job_status(animation.job_id)
    if status == "finished" and animation.status != "complete":
        animation.status = "complete"
        animation.save()

    return JsonResponse({"status": animation.status})

@login_required
def youtube_video_list(request):
    """Youtube videos list, for generating videos from youtube."""
    form = None
    if request.method == "POST":
        form = YouTubeDownloadForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data["youtube_url"]
            start_time = form.cleaned_data["start_time"]
            end_time = form.cleaned_data["end_time"]
            output_name = form.cleaned_data["video_name"]

            form = None
            return download_and_trim_youtube_video(
                request, url, start_time, end_time, output_name
            )
    if not form:
        form = YouTubeDownloadForm()
    return render(request, "mkgif/youtube.html", {"form": form})

@login_required
def music_list(request):
    """Create mp3."""
    if request.method == "POST":
        form = MusicDownloadForm(request.POST, request.FILES)
        if form.is_valid():
            music_file = request.FILES["music_file"]
            music_file_name = form.cleaned_data["music_file_name"]

            # Enqueue the conversion task and get the job ID
            job_id = convert_mp4_to_mp3(music_file, music_file_name)

            # Return the job ID to the client
            return JsonResponse(
                {
                    "job_id": job_id,
                }
            )

    else:
        form = MusicDownloadForm()

    return render(request, "mkgif/music.html", {"form": form})

@login_required
def file(request, job_id):
    """Download file."""

    status_record = Job.objects.get(job_id=job_id)
    file_path = status_record.file_path

    response = FileResponse(open(file_path, "rb"))
    response[
        "Content-Disposition"
    ] = f'attachment; filename="{os.path.basename(file_path)}"'

    Job.objects.get(job_id=job_id).delete()
    return response
