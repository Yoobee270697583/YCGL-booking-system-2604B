import datetime
import uuid

from django.core.exceptions import ValidationError

from django.db import models

# Room hours: earliest start 8:30am, latest end 9:00pm, in 15-minute steps
EARLIEST_START = datetime.time(8, 30)
LATEST_START = datetime.time(20, 45)
EARLIEST_END = datetime.time(8, 45)
LATEST_END = datetime.time(21, 0)

# Helper function, returns a list of every 15 minute increment passed into it
def on_quarter_hour(t):
    return t.minute % 15 == 0 and t.second == 0


# Model for setting in dates that the clubroom cannot be booked - a "blackout" period on the calendar
class BlackoutPeriod(models.Model):
    first_date = models.DateField()
    last_date = models.DateField()
    note = models.CharField(max_length=200, blank=True)

    # Method to calculate and display clubroom closure dates to users
    def __str__(self):
        if self.first_date == self.last_date:
            return f"Closed {self.first_date}"
        return f"Closed {self.first_date} to {self.last_date}"
    
    # Validation method to enforce correct date choices when admins are setting in blackout periods, and show a relevent error message when needed
    def clean(self):
        if self.first_date and self.last_date and self.last_date < self.first_date:
            raise ValidationError(
                {"last_date": "The last date can't be before the first date."}
            )


# Model for defining and handling bookings
class Booking(models.Model):
    #Subclass to define the status of a booking, as text
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"
        CANCELLED = "cancelled", "Cancelled"

    # Booknng data, recieved from booking form fields
    # Who is applying
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    # What and when applicant wants the clubroom for
    purpose = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    # The current status of the booking application
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    # It's unique key, randomly generated using uuid
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    # When it was made
    created_at = models.DateTimeField(auto_now_add=True)

    # String method - returns a bookings details as a string
    def __str__(self):
        return f"{self.name} - {self.date} {self.start_time:%H:%M}-{self.end_time:%H:%M} ({self.status})"

    # Method to find the reason for a booking conflict
    # None if the slot is free, otherwise return either "blackout" or "booked"
    def conflict_reason(self):
        
        # Check a booking against existing blackout periods
        blackout = BlackoutPeriod.objects.filter(
            first_date__lte=self.date, last_date__gte=self.date
        )
        # If yes, return the reason
        if blackout.exists():
            return "blackout"
        return None

        # Check a booking against other existing bookings
        clashing = Booking.objects.filter(
            status=Booking.Status.APPROVED,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)
        # If yes, return the reason
        if clashing.exists():
            return "booked"
        return None

    # Method to figure if there is a booking conflict, for any reason. True or False
    def has_conflict(self):
        return self.conflict_reason() is not None


    # Booking model level validation method
    def clean(self):
        #Builds an errors dictionary to display input errors to the user on the form
        errors = {}
        
        # Bookings must have either a Yoobee StudentID or email address
        if not self.student_id and not self.email:
            errors["student_id"] = (
                "Please enter either your Yoobee email, Yoobee Student ID, or both."
            )

        # Bookings must comply with 15 minute increments, including the start time
        if self.start_time is not None:
            if not on_quarter_hour(self.start_time):
                errors["start_time"] = "The start time must be on the hour or a quarter past, half past or quarter to."
            elif not (EARLIEST_START <= self.start_time <= LATEST_START):
                errors["start_time"] = "Booking start times must be between 8:30am and 8:45pm."

        # Bookings must comply with 15 minute increments, including the end time
        if self.end_time is not None:
            if not on_quarter_hour(self.end_time):
                errors["end_time"] = "The end time must be on the hour or a quarter past, half past or quarter to."
            elif not (EARLIEST_END <= self.end_time <= LATEST_END):
                errors["end_time"] = "Booking end times must be between 8:45am and 9:00pm."

        # Bookings must not end before they begin
        if (
            self.start_time is not None
            and self.end_time is not None
            and "end_time" not in errors
            and self.end_time <= self.start_time
        ):
            errors["end_time"] = "Bookings can't end before they start... are you sure your times are entered correctly?"

        # Bookings must not have a conflict with a blackout period or another booking
        if (
            "start_time" not in errors
            and "end_time" not in errors
            and self.status in (self.Status.PENDING, self.Status.APPROVED)
            and self.date is not None
            and self.start_time is not None
            and self.end_time is not None
        ):
            reason = self.conflict_reason()
            if reason == "blackout":
                errors["date"] = "The clubroom is closed on that date."
            elif reason == "booked":
                errors["start_time"] = "The Clubroom is already booked at that time. Check the Room Bookings page for details"

        if errors:
            raise ValidationError(errors)