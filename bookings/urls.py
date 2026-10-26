from django.urls import path

# The views.py file, where the functions each URL points to are defined
from . import views

# The list Django checks, in order, to match a requested URL to a view function
# name= gives each route a label, so templates ({% url 'week' %}) and redirect() can find it without hard-coding the address
urlpatterns = [
    # The home page: the booking application form
    path("", views.apply, name="apply"),
    # The week-by-week calendar of approved bookings
    path("week/", views.week, name="week"),
    # The endpoint availability.js calls to check whether a slot is free
    path("check/", views.check, name="check"),
    # A booking's status page. <uuid:token> captures the unguessable code from the address and passes it to the view as 'token'
    path("booking/<uuid:token>/", views.status, name="status"),
]