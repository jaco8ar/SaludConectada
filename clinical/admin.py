from django.contrib import admin
from .models import MedicalRecord, Consultation


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ("patient",)


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ("appointment", "created_at", "updated_at")
    search_fields = ("appointment__patient__username", "appointment__doctor__username")

