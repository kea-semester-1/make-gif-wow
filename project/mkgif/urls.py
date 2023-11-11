from django.urls import path
from . import views


app_name = "mkgif"

urlpatterns = [
    path("", views.index, name="index"),
    path("animation/", views.animation, name="animation"),
    path("animation/<int:pk>/", views.animation_details, name="animation_details"),
    path(
        "animation-detail/<int:pk>/",
        views.animation_details_list,
        name="animation_detail_list",
    ),
    path("status/<int:pk>/", views.status, name="status"),
]
