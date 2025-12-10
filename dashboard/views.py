
from django.contrib import messages
from .forms import UserRoleForm
from accounts.decorators import role_required
from accounts.models import User
from clinical.models import Consultation
from scheduling.models import Appointment
from django.shortcuts import get_object_or_404, redirect, render
from scheduling.models import DoctorAvailability
from datetime import time


@role_required(User.Roles.PATIENT)
def patient_dashboard(request):
    """
    Panel del paciente:
    - Próximas citas.
    - Acceso rápido a historial y videollamadas.
    """
    upcoming_appointments = (
        Appointment.objects
        .filter(patient=request.user, status__in=[
            Appointment.Status.PENDING,
            Appointment.Status.CONFIRMED,
            Appointment.Status.IN_PROGRESS,
        ])
        .order_by("scheduled_datetime")[:5]
    )

    # Última consulta (para simular la idea de seguimiento)
    last_consultation = (
        Consultation.objects
        .filter(appointment__patient=request.user)
        .order_by("-created_at")
        .first()
    )

    context = {
        "upcoming_appointments": upcoming_appointments,
        "last_consultation": last_consultation,
    }
    return render(request, "dashboard/patient_dashboard.html", context)


@role_required(User.Roles.DOCTOR)
def doctor_dashboard(request):
    """
    Panel del médico:
    - Próximas citas asignadas.
    - Link a citas y a futuros módulos de disponibilidad.
    """
    upcoming_appointments = (
        Appointment.objects
        .filter(doctor=request.user, status__in=[
            Appointment.Status.PENDING,
            Appointment.Status.CONFIRMED,
            Appointment.Status.IN_PROGRESS,
        ])
        .order_by("scheduled_datetime")[:10]
    )

    context = {
        "upcoming_appointments": upcoming_appointments,
    }
    return render(request, "dashboard/doctor_dashboard.html", context)


@role_required(User.Roles.ADMIN)
def admin_dashboard(request):
    """
    Panel del administrador:
    - Métricas básicas de uso.
    - Placeholders para supervisar uso, sincronización externa y reportes.
    """
    total_users = User.objects.count()
    patients_count = User.objects.filter(role=User.Roles.PATIENT).count()
    doctors_count = User.objects.filter(role=User.Roles.DOCTOR).count()
    admins_count = User.objects.filter(role=User.Roles.ADMIN).count()

    total_appointments = Appointment.objects.count()
    appointments_by_status = {
        status_label: Appointment.objects.filter(status=status_value).count()
        for status_value, status_label in Appointment.Status.choices
    }

    context = {
        "total_users": total_users,
        "patients_count": patients_count,
        "doctors_count": doctors_count,
        "admins_count": admins_count,
        "total_appointments": total_appointments,
        "appointments_by_status": appointments_by_status,
    }
    return render(request, "dashboard/admin_dashboard.html", context)


# --- Placeholders “avanzados”


@role_required(User.Roles.ADMIN)
def system_usage_placeholder(request):
    """
    Placeholder para 'Supervisar uso del sistema'.
    En el futuro aquí podríamos mostrar gráficas reales, logs, etc.
    """
    # TODO: integrar métricas reales (p. ej. número de logins por día, etc.)
    return render(request, "dashboard/system_usage.html")


@role_required(User.Roles.ADMIN)
def external_sync_placeholder(request):
    """
    Placeholder para 'Sincronizar con sistemas externos'.
    Por ahora solo mostramos un mensaje.
    """
    if request.method == "POST":
        # Aquí en el futuro se llamaría a un servicio real de integración
        messages.info(
            request,
            "Simulación: se habría iniciado la sincronización con el sistema externo.",
        )

    return render(request, "dashboard/external_sync.html")


@role_required(User.Roles.ADMIN)
def reports_placeholder(request):
    """
    Placeholder para generación/descarga de reportes.
    Más adelante: generar PDF/Excel.
    """
    # Aquí podríamos construir un dataset simple para mostrar en pantalla
    appointments = (
        Appointment.objects
        .select_related("patient", "doctor")
        .order_by("-scheduled_datetime")[:20]
    )

    context = {
        "appointments": appointments,
    }
    return render(request, "dashboard/reports.html", context)

@role_required(User.Roles.ADMIN)
def manage_users(request):
    users = User.objects.all().order_by("id")

    # Construimos (user, form) para el GET
    user_forms = [
        (user, UserRoleForm(initial={"role": user.role}))
        for user in users
    ]

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        target_user = get_object_or_404(User, pk=user_id)

        form = UserRoleForm(request.POST)
        if form.is_valid():
            new_role = form.cleaned_data["role"]

            # 1) Evitar que un admin se auto-degrade
            if target_user == request.user and new_role != User.Roles.ADMIN:
                messages.error(
                    request,
                    "No puedes cambiar tu propio rol a uno distinto de Administrador."
                )
                return redirect("dashboard:manage_users")

            # 2) Si lo estamos convirtiendo en MÉDICO, asegurar disponibilidad mínima
            if new_role == User.Roles.DOCTOR and target_user.role != User.Roles.DOCTOR:
                has_active_avail = DoctorAvailability.objects.filter(
                    doctor=target_user,
                    is_active=True,
                ).exists()

                if not has_active_avail:
                    default_days = [
                        DoctorAvailability.Weekday.MONDAY,
                        DoctorAvailability.Weekday.TUESDAY,
                        DoctorAvailability.Weekday.WEDNESDAY,
                        DoctorAvailability.Weekday.THURSDAY,
                        DoctorAvailability.Weekday.FRIDAY,
                    ]
                    for day in default_days:
                        DoctorAvailability.objects.create(
                            doctor=target_user,
                            weekday=day,
                            start_time=time(8, 0),
                            end_time=time(12, 0),
                            is_active=True,
                        )
                    messages.info(
                        request,
                        "El usuario ahora es Médico. "
                        "Se ha creado una disponibilidad básica de Lunes a Viernes, 08:00–12:00. "
                        "El médico podrá ajustarla luego en su panel."
                    )

            # Aplicar cambio de rol
            target_user.role = new_role
            target_user.save()
            messages.success(request, "Rol actualizado correctamente.")
            return redirect("dashboard:manage_users")

        # Si el form no es válido, caería aquí (poco probable)
        messages.error(request, "El formulario enviado no es válido.")
        return redirect("dashboard:manage_users")

    context = {
        "user_forms": user_forms,
    }
    return render(request, "dashboard/manage_users.html", context)


