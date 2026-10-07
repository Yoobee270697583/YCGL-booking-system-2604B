from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm
from .models import Booking


def apply(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            return redirect("status", token=booking.token)
    else:
        form = BookingForm()
    return render(request, "bookings/apply.html", {"form": form})


def status(request, token):
    booking = get_object_or_404(Booking, token=token)
    return render(request, "bookings/status.html", {"booking": booking})