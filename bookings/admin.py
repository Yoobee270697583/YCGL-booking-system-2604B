from django.contrib import admin, messages

from .models import Booking, BlackoutPeriod


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    ordering = ("date", "start_time")
    readonly_fields = ("token", "created_at")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        newly_approved = obj.status == Booking.Status.APPROVED and (
            not change or "status" in form.changed_data
        )
        if not newly_approved:
            return

        clashing = Booking.objects.filter(
            status=Booking.Status.PENDING,
            date=obj.date,
            start_time__lt=obj.end_time,
            end_time__gt=obj.start_time,
        ).exclude(pk=obj.pk)

        count = 0
        for other in clashing:
            other.status = Booking.Status.DECLINED
            other.save(update_fields=["status"])
            self.log_change(
                request,
                other,
                "Automatically declined: it overlaps a booking that was just approved.",
            )
            count += 1

        if count:
            self.message_user(
                request,
                f"{count} overlapping pending application(s) declined automatically.",
                messages.WARNING,
            )


@admin.register(BlackoutPeriod)
class BlackoutPeriodAdmin(admin.ModelAdmin):
    ordering = ("first_date",)