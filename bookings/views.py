import datetime

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import BookingForm
from .models import BlackoutPeriod, Booking
from .window import window_message


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


def week(request):
    try:
        chosen = datetime.date.fromisoformat(request.GET.get("start", ""))
    except ValueError:
        chosen = timezone.localdate()

    monday = chosen - datetime.timedelta(days=chosen.weekday())
    sunday = monday + datetime.timedelta(days=6)

    approved = Booking.objects.filter(
        status=Booking.Status.APPROVED, date__range=(monday, sunday)
    ).order_by("start_time")
    blackouts = BlackoutPeriod.objects.filter(
        first_date__lte=sunday, last_date__gte=monday
    )

    days = []
    for i in range(7):
        day = monday + datetime.timedelta(days=i)
        days.append(
            {
                "date": day,
                "bookings": [b for b in approved if b.date == day],
                "closed": any(b.first_date <= day <= b.last_date for b in blackouts),
            }
        )

    return render(
        request,
        "bookings/week.html",
        {
            "days": days,
            "monday": monday,
            "sunday": sunday,
            "prev_monday": monday - datetime.timedelta(days=7),
            "next_monday": monday + datetime.timedelta(days=7),
        },
    )

def check(request):
    try:
        date = datetime.date.fromisoformat(request.GET.get("date", ""))
        start = datetime.time.fromisoformat(request.GET.get("start", ""))
        end = datetime.time.fromisoformat(request.GET.get("end", ""))
    except ValueError:
        return JsonResponse({"state": "incomplete"})

    message = window_message(date)
    if message:
        return JsonResponse({"state": "window", "message": message})

    if end <= start:
        return JsonResponse({"state": "order"})

    reason = Booking(date=date, start_time=start, end_time=end).conflict_reason()
    return JsonResponse({"state": reason or "free"})