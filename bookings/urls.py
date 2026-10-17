from django.urls import path

from . import views

urlpatterns = [
    path("", views.apply, name="apply"),
    path("week/", views.week, name="week"),
    path("check/", views.check, name="check"),
    path("booking/<uuid:token>/", views.status, name="status"),
]