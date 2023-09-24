from .models import Animation, Image
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    if request.method == "POST":
        anim = Animation.objects.create(name=request.POST["name"], user=request.user)
        for img in request.FILES.getlist("imgs"):
            Image.objects.create(animation=anim, image=img)
        anim.enqueue(
            {"framerate": request.POST["framerate"], "scale": request.POST["scale"]}
        )

    anims = Animation.objects.all().filter(user=request.user)
    context = {"anims": anims}
    return render(request, "mkgif/index.html", context)


@login_required
def details(request, pk):
    anim = get_object_or_404(Animation, pk=pk)
    images = Image.objects.filter(animation=pk)
    context = {"anim": anim, "images": images}
    return render(request, "mkgif/details.html", context)


@login_required
def gifs(request, pk):
    anim = get_object_or_404(Animation, pk=pk)
    anim.delete()

    anims = Animation.objects.all()
    context = {"anims": anims}
    return render(request, "mkgif/index.html", context)


@login_required
def make_gif(request, pk):
    anim = get_object_or_404(Animation, pk=pk)

    name = request.POST.get("name", None)
    if name:
        Animation.objects.filter(pk=pk).update(name=name)
    anim.enqueue(
        {"framerate": request.POST["framerate"], "scale": request.POST["scale"]}
    )
    anims = Animation.objects.all()
    context = {"anims": anims}
    return render(request, "mkgif/index.html", context)
