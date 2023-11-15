from .models import Animation, Image
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.contrib.auth.decorators import login_required
from mkgif.forms import AnimationForm
from django.http import HttpResponseRedirect
from mkgif.utils import get_job_status
from django.http import JsonResponse
from django.core.paginator import Paginator


def index(request):
    return HttpResponseRedirect(reverse("mkgif:animation"))


@login_required
def animation(request):
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
    animation = Animation.objects.get(pk=pk)
    status = get_job_status(animation.job_id)
    print(animation.status)
    print(status)
    if status == "finished" and animation.status != "complete":
        animation.status = "complete"
        animation.save()

    return JsonResponse({"status": animation.status})
