from datetime import date, datetime, timedelta

from django import forms

# Import 4 clubroom times as constants, and bookings object
from .models import (
    EARLIEST_END,
    EARLIEST_START,
    LATEST_END,
    LATEST_START,
    Booking,
)
from .window import application_window_message


# Function for the Booking Form. Sets available times to 15 minute increments within the acceptable time of day (8:30am - 9:00pm)
# Pass in the first and last possible choice for a timeslot dropdown, taken from the clubroom times defined as constants in models.py
def calculate_timeslots(first, last):
    # Make a list to save all possible options
    options = [("", "Choose a time")]
    # Convert start and end times into a data type that can be incremented by a timedelta (because a time() cannot be)
    current_slot = datetime.combine(date.today(), first)
    final_slot = datetime.combine(date.today(), last)

    # Loop through every 15 minute increment between the first and last, including the last, times passed in
    while current_slot <= final_slot:
        # Format each increment twice, once as a 24-hour text value to send server-side, and once as a 12-hour text value to show
        value_sent = current_slot.strftime("%H:%M")
        label_shown = current_slot.strftime("%I:%M %p").lstrip("0")
        # Append each increment to the list of options
        options.append((value_sent, label_shown))
        # And loop again
        current_slot += timedelta(minutes=15)
    # Return the list of options
    return options

# The Booking application form, built from the booking model, to show on apply.html
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "name",
            "student_id",
            "email",
            "purpose",
            "date",
            "start_time",
            "end_time",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.Select(choices=calculate_timeslots(EARLIEST_START, LATEST_START)),
            "end_time": forms.Select(choices=calculate_timeslots(EARLIEST_END, LATEST_END)),
        }

    # A method that Django runs automatically because of how it is named, on the "date" field during validation
    # Django calls any method named clean_<fieldname> automatically on the form's validation pass (is_valid() method provided by Django forms)
    def clean_date(self):
        # The date the user entered, already converted into a date object by Django
        date = self.cleaned_data["date"]
        # Run application_window_message, imported from window.py
        # The result will either be None if applications are open for date passed in, or a message explaining why not
        message = application_window_message(date)
        # If there is a problem with the date passed in for a booking
        if message:
            # Then the clean_date() method stops here and an appropriate error message to display is added to the date field
            raise forms.ValidationError(message)
        # Otherwise, the date is returned if it's compatible for the current booking window
        return date