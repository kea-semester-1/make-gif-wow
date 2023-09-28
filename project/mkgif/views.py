from .models import Animation, Image
from django.shortcuts import render, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from mkgif.forms import AnimationForm
from django.http import HttpResponseRedirect
from mkgif.utils import get_job_status


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
            for img in request.FILES.getlist("imgs"):
                Image.objects.create(animation=anim, image=img)

            anim.enqueue(
                {
                    "framerate": animation_form.cleaned_data["framerate"],
                    "scale": animation_form.cleaned_data["scale"],
                    "from_format": animation_form.cleaned_data["select_type_from"],
                    "to_format": animation_form.cleaned_data["select_type_to"],
                }
            )
            animation_form = None

    if not animation_form:
        animation_form = AnimationForm()

    anims = Animation.objects.filter(user=request.user)
    context = {"anims": anims, "animation_form": animation_form}
    return render(request, "mkgif/index.html", context)


@login_required
def details(request, pk):
    anim = get_object_or_404(Animation, pk=pk, user=request.user)
    images = Image.objects.filter(animation=pk)
    context = {"anim": anim, "images": images}
    return render(request, "mkgif/details.html", context)


@login_required
def gifs(request, pk):
    anim = get_object_or_404(Animation, pk=pk)

    # Delete the associated Image objects and their physical files
    for image in anim.image_set.all():
        image.delete(anim.pk)

    # Delete the Animation object
    anim.delete()

    anims = Animation.objects.all()
    context = {"anims": anims}
    return render(request, "mkgif/index.html", context)


@login_required
def make_gif(request, pk):
    anim = get_object_or_404(Animation, pk=pk)

    name = request.POST.get("name", None)
    framerate = request.POST["framerate"]
    scale = request.POST["scale"]

    if name:
        Animation.objects.filter(pk=pk).update(name=name)
    anim.enqueue(params={"framerate": framerate, "scale": scale})
    anims = Animation.objects.all()
    context = {"anims": anims}
    return render(request, "mkgif/index.html", context)


from django.http import JsonResponse


@login_required
def check_status(request, pk):
    animation = Animation.objects.get(pk=pk)
    status = get_job_status(animation.job_id)
    print(animation.status)
    print(status)
    if status == "finished" and animation.status != "complete":
        animation.status = "complete"
        animation.save()

    return JsonResponse({"status": animation.status})
