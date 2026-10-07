from django import forms

from .models import Booking


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
            "start_time": forms.TimeInput(attrs={"type": "time", "step": 900}),
            "end_time": forms.TimeInput(attrs={"type": "time", "step": 900}),
        }