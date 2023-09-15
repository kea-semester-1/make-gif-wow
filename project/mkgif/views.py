from .models import Animation, Image
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    if request.method == 'POST':
        anim = Animation.objects.create(name=request.POST['name'])
        for img in request.FILES.getlist('imgs'):
            Image.objects.create(animation=anim, image=img)

    anims = Animation.objects.all()
    context = {
            'anims': anims
            }
    return render(request, 'mkgif/index.html', context)

@login_required
def details(request, pk):
    anim = get_object_or_404(Animation, pk=pk)
    images = Image.objects.filter(animation=pk)
    context = {
            'anim': anim,
            'images': images
            }
    return render(request, 'mkgif/details.html', context)

