from django.urls import path
from . import views


app_name = 'mkgif'

urlpatterns = [
    path('', views.index, name='index'),
    path('details/<int:pk>/', views.details, name='details'),
]

