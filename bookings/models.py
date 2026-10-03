import datetime
import uuid

from django.core.exceptions import ValidationError
from django.db import models

# Room hours: earliest start 8:30am, latest end 9:00pm, in 15-minute steps
EARLIEST_START = datetime.time(8, 30)
LATEST_START = datetime.time(20, 45)
EARLIEST_END = datetime.time(8, 45)
LATEST_END = datetime.time(21, 0)


def on_quarter_hour(t):
    return t.minute % 15 == 0 and t.second == 0


class BlackoutPeriod(models.Model):
    first_date = models.DateField()
    last_date = models.DateField()
    note = models.CharField(max_length=200, blank=True)

    def __str__(self):
        if self.first_date == self.last_date:
            return f"Closed {self.first_date}"
        return f"Closed {self.first_date} to {self.last_date}"

    def clean(self):
        if self.first_date and self.last_date and self.last_date < self.first_date:
            raise ValidationError(
                {"last_date": "The last date can't be before the first date."}
            )


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DECLINED = "declined", "Declined"
        CANCELLED = "cancelled", "Cancelled"

    # Who is applying
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    # What they want
    purpose = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    # Where the application stands
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.date} {self.start_time:%H:%M}-{self.end_time:%H:%M} ({self.status})"


    def conflict_reason(self):
        """None if the slot is free, otherwise "blackout" or "booked"."""
        if BlackoutPeriod.objects.filter(
            first_date__lte=self.date, last_date__gte=self.date
        ).exists():
            return "blackout"

        clashing = Booking.objects.filter(
            status=Booking.Status.APPROVED,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)
        if clashing.exists():
            return "booked"

            return None

    def has_conflict(self):
        return self.conflict_reason() is not None


    def clean(self):
        errors = {}

        if not self.student_id and not self.email:
            errors["student_id"] = (
                "Enter your Yoobee student ID, your Yoobee email, or both."
            )

        if self.start_time is not None:
            if not on_quarter_hour(self.start_time):
                errors["start_time"] = "The start time must be on the hour or a quarter past, half past or quarter to."
            elif not (EARLIEST_START <= self.start_time <= LATEST_START):
                errors["start_time"] = "Booking start times must be between 8:30am and 8:45pm."

        if self.end_time is not None:
            if not on_quarter_hour(self.end_time):
                errors["end_time"] = "The end time must be on the hour or a quarter past, half past or quarter to."
            elif not (EARLIEST_END <= self.end_time <= LATEST_END):
                errors["end_time"] = "Booking end times must be between 8:45am and 9:00pm."

        if (
            self.start_time is not None
            and self.end_time is not None
            and "end_time" not in errors
            and self.end_time <= self.start_time
        ):
            errors["end_time"] = "Bookings can't end after they start... are you sure your times are entered correctly?"

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
                errors["date"] = "The YCGL clubroom is closed on that date."
            elif reason == "booked":
                errors["start_time"] = "The Clubroom is already booked at that time. Check the Room Bookings page for details"

        if errors:
            raise ValidationError(errors)