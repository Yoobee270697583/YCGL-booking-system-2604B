from django.contrib import admin

from .models import BlackoutPeriod, Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    ordering = ("date", "start_time")
    readonly_fields = ("token", "created_at")


@admin.register(BlackoutPeriod)
class BlackoutPeriodAdmin(admin.ModelAdmin):
    ordering = ("first_date",)

