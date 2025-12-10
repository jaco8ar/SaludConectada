from django.contrib import admin
from .models import Appointment


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

