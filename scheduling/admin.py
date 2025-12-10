from django.contrib import admin
from .models import Appointment, DoctorAvailability


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "doctor",
        "scheduled_datetime",
        "status",
        "created_at",
        "canceled_at",
    )
    list_filter = ("status", "doctor")
    search_fields = ("patient__username", "doctor__username")

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ("doctor", "weekday", "start_time", "end_time", "is_active")
    list_filter = ("doctor", "weekday", "is_active")