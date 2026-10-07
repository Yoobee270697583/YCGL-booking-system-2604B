from django.urls import path

from . import views

urlpatterns = [
    path("", views.apply, name="apply"),
    path("booking/<uuid:token>/", views.status, name="status"),
]