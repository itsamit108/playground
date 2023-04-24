from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("current_datetime/", views.current_datetime, name="current_datetime"),
]
