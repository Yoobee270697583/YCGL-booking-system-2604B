import datetime

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

# imports from other custom modules
from .forms import BookingForm
from .models import BlackoutPeriod, Booking
from .window import open_week_monday, application_window_message


# Define the view for the main booking applications page
def apply(request):
    # If the form was submitted (a POST request)
    if request.method == "POST":
        # Save the data sent by the request to a variable
        form = BookingForm(request.POST)
        # Then check if the data sent passes validation, using the is_valid() method provided by Django forms
        if form.is_valid():
            # If yes check if the honeypot field was filled (a real person never sees this field).
            if request.POST.get("website"):
                # If it was filled, do the following: pretend it worked, save nothing.
                return render(request, "bookings/status.html", {"booking": form.instance})
            booking = form.save()
            # Then redirect to the booking status view
            return redirect("status", token=booking.token)
        # If the data sent doesn't pass validation, the else below doesn't happen and the code continues on from the following return render()
    
    # When the form wasn't submitted (a GET request)
    else:
        # Create an empty form
        form = BookingForm()
    # Set Monday and Sunday dates as variables, to display which week is currently open for bookings on apply.html
    monday = open_week_monday(timezone.localdate())
    sunday = monday + datetime.timedelta(days=6)
    # Render the application form and pass it the dates of the week open for applications
    return render(
        request,
        "bookings/apply.html",
        {"form": form, "monday": monday, "sunday": sunday},
    )

# Define view for the booking status page
def status(request, token):
    booking = get_object_or_404(Booking, token=token)
    return render(request, "bookings/status.html", {"booking": booking})

# Define view for the bookings-calendar page
def week(request):
    try:
        chosen = datetime.date.fromisoformat(request.GET.get("start", ""))
    except ValueError:
        chosen = timezone.localdate()

    # Save Monday and Sunday dates to variables
    monday = chosen - datetime.timedelta(days=chosen.weekday())
    sunday = monday + datetime.timedelta(days=6)

    # Set a variable of already approved bookings for the week being displayed, ordered by start time
    approved = Booking.objects.filter(
        status=Booking.Status.APPROVED, date__range=(monday, sunday)
    ).order_by("start_time")

    # Set a variable of existing blackout periods for the week currently being displayed
    blackouts = BlackoutPeriod.objects.filter(
        first_date__lte=sunday, last_date__gte=monday
    )

    # Build a list of 7 dictionaries, 1 for each day of the week. 
    days = []
    for i in range(7):
        day = monday + datetime.timedelta(days=i)
         # Each dictionary contains a date, any confirmed bookings for that day, and whether the room is closed that day.
        days.append(
            {
                "date": day,
                "bookings": [b for b in approved if b.date == day],
                "closed": any(b.first_date <= day <= b.last_date for b in blackouts),
            }
        )

    # After the bookings data for the current week being shown is filtered for and organised above:
    # Send back a response with the data for rendering the template and the week/calendar navigation buttons
    return render(
        request,                                                    # Request object
        "bookings/week.html",                                       # Template to render it on
        {
            "days": days,                                           # 7 days of the week
            "monday": monday,                                       # Date of the Monday
            "sunday": sunday,                                       # Date of the Sunday
            "prev_monday": monday - datetime.timedelta(days=7),     # For the previous week nav button  
            "next_monday": monday + datetime.timedelta(days=7),     # For the following week nav button
        },
    )

# Define an endpoint for availability.js to use for checking clubroom availability
def check(request):
    # Make 3 objects from the query data sent, for later use
    try:
        date = datetime.date.fromisoformat(request.GET.get("date", ""))
        start = datetime.time.fromisoformat(request.GET.get("start", ""))
        end = datetime.time.fromisoformat(request.GET.get("end", ""))
    # Whenever any of them don't hold the proper value, nothing else below runs
    except ValueError:
        # And tell availability.js to clear its message box until all 3 hold appropriate values
        return JsonResponse({"state": "incomplete"})

    # Check if the user's currently selected date is within the currently open application window, and save an appropriate message if not
    message = application_window_message(date)
    if message:
        # Return JSON with key : value pairs that availability.js will use to show the message, and apply appropriate bootstrap classes to it
        return JsonResponse({"state": "window", "message": message})
    # Likewise, if a user enters an application time that ends before it starts
    if end <= start:
        return JsonResponse({"state": "order"})

    # Check if the user's currently selected date and times conflict with any other bookings or blackout periods
    # And if they do, save the reason for a conflict
    reason = Booking(date=date, start_time=start, end_time=end).conflict_reason()
    # Return JSON with key : value pairs that availability.js will use to show the message, and apply appropriate bootstrap classes to it
    return JsonResponse({"state": reason or "free"})