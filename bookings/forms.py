from django import forms

from .models import Booking
from .window import window_message


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
        
    def clean_date(self):
        date = self.cleaned_data["date"]
        message = window_message(date)
        if message:
            raise forms.ValidationError(message)
        return date