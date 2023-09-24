from django.urls import path
from . import views


app_name = "mkgif"

urlpatterns = [
    path("", views.index, name="index"),
    path("details/<int:pk>/", views.details, name="details"),
    path("gifs/<int:pk>/", views.gifs, name="gif_pk"),
    path("make_gif/<int:pk>/", views.make_gif, name="make_gif"),
]
