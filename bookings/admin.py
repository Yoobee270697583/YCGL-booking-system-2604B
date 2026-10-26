from django.contrib import admin, messages

from .models import Booking, BlackoutPeriod

# Show the Booking model in the Django admin area
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    ordering = ("date", "start_time")           # Sort Bookings by date then start time
    readonly_fields = ("token", "created_at")   # Show these fields but site admins can't edit them

    # Method to save a Booking object whenever an admin saves a booking in the Django admin portal
    # save_model already exists in ModelAdmin. I'm overriding it here in order to add my auto-decline functionality
    # When a booking is approved, the override automatically declines any other pending bookings that would clash with the one that just got approved
    def save_model(self, request, obj, form, change):
        # Run the normal save first. This is because a booking has to be saved with it's updated data before it can be chacked against for any clashing applications
        super().save_model(request, obj, form, change)

        # If the status of the booking we are working with isn't approved
        if obj.status != Booking.Status.APPROVED:
            # The method stops here with return
            return
        # This is because only approved bookings can clash with other bookings
        # And therefore only approved bookings need the rest of the method as below

        # Find/filter for overlapping booking applications on the same date and save them to the variable called clashing
        clashing = Booking.objects.filter(
            status=Booking.Status.PENDING,
            date=obj.date,
            start_time__lt=obj.end_time,
            end_time__gt=obj.start_time,
        # Excluding the booking currently being dealt with
        ).exclude(pk=obj.pk)

        # Loop through all the overlapping booking applications
        # Count how many there were to report back to the admin user
        count = 0
        for other in clashing:
            # Decline the booking and save only the status column
            other.status = Booking.Status.DECLINED
            other.save(update_fields=["status"])
            # And add the reason to the object's log
            self.log_change(
                request,
                other,
                "Automatically declined: it overlaps an approved booking.",
            )
            count += 1

        # If any were declined, show a warning on the admin page
        if count:
            self.message_user(
                request,
                f"{count} overlapping pending application(s) declined automatically.",
                messages.WARNING,
            )

# Show Blackout Periods in the Admin area
@admin.register(BlackoutPeriod)
class BlackoutPeriodAdmin(admin.ModelAdmin):
    ordering = ("first_date",)                  # Sorted by the first date of the blackout period