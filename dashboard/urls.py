from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("paciente/panel/", views.patient_dashboard, name="patient_dashboard"),
    path("medico/panel/", views.doctor_dashboard, name="doctor_dashboard"),
    path("admin/panel/", views.admin_dashboard, name="admin_dashboard"),

    # Placeholders
    path("sistema/uso/", views.system_usage_placeholder, name="system_usage"),
    path("sistema/sincronizacion-externa/", views.external_sync_placeholder, name="external_sync"),
    path("sistema/reportes/", views.reports_placeholder, name="reports"),
]
