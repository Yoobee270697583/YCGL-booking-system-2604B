import datetime

from django import forms

from .models import (
    EARLIEST_END,
    EARLIEST_START,
    LATEST_END,
    LATEST_START,
    Booking,
)
from .window import window_message


# Helper method for the Booking Form. Helps to set available times to 15 minute increments
def time_choices(first, last):
    # Dropdown options every 15 minutes from `first` to `last`, inclusive.
    choices = [("", "Choose a time")]
    minutes = first.hour * 60 + first.minute
    last_minutes = last.hour * 60 + last.minute
    while minutes <= last_minutes:
        t = datetime.time(minutes // 60, minutes % 60)
        choices.append((t.strftime("%H:%M"), t.strftime("%I:%M %p").lstrip("0")))
        minutes += 15
    return choices

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
            "start_time": forms.Select(choices=time_choices(EARLIEST_START, LATEST_START)),
            "end_time": forms.Select(choices=time_choices(EARLIEST_END, LATEST_END)),
        }
        
    def clean_date(self):
        date = self.cleaned_data["date"]
        message = window_message(date)
        if message:
            raise forms.ValidationError(message)
        return date