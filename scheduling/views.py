from django.shortcuts import render

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from accounts.decorators import role_required
from accounts.models import User
from .forms import (
    AppointmentSearchForm,
    AppointmentSlotForm,
    DoctorAvailabilityForm,
)
from .models import Appointment, DoctorAvailability
from .utils import get_available_slots_for_doctor_and_date
from collections import defaultdict


@role_required(User.Roles.PATIENT)
def patient_appointments(request):
    """
    Lista de citas del paciente.
    La creación ahora se hace en un flujo separado por slots.
    """
    appointments = (
        Appointment.objects
        .filter(patient=request.user)
        .select_related("doctor")
        .order_by("scheduled_datetime")
    )
    return render(request, "scheduling/patient_appointments.html", {"appointments": appointments})

@role_required(User.Roles.PATIENT)
def new_appointment_step1(request):
    """
    Paso 1: el paciente elige médico y fecha.
    Además mostramos la disponibilidad semanal típica de los médicos.
    """
    # 1) Prellenar con lo que venga de GET (para cuando volvemos del paso 2)
    initial = {}
    doctor_id = request.GET.get("doctor")
    date_str = request.GET.get("date")

    if doctor_id:
        initial["doctor"] = doctor_id
    if date_str:
        try:
            initial["date"] = datetime.fromisoformat(date_str).date()
        except ValueError:
            pass

    if request.method == "POST":
        form = AppointmentSearchForm(request.POST)
        if form.is_valid():
            doctor = form.cleaned_data["doctor"]
            date = form.cleaned_data["date"]
            return redirect(
                f"{reverse('scheduling:new_appointment_step2')}?doctor={doctor.pk}&date={date.isoformat()}"
            )
    else:
        form = AppointmentSearchForm(initial=initial)

    # 2) Construir disponibilidad típica de cada médico
    doctors = (
        User.objects
        .filter(role=User.Roles.DOCTOR)
        .prefetch_related("availabilities")
    )

    doctors_availability = []
    for doctor in doctors:
        # Solo disponibilidades activas
        avail_qs = doctor.availabilities.filter(is_active=True).order_by("weekday", "start_time")
        day_map = defaultdict(list)  # { "Lunes": ["08:00–12:00", ...], ... }

        for avail in avail_qs:
            label = f"{avail.start_time.strftime('%H:%M')}–{avail.end_time.strftime('%H:%M')}"
            day_map[avail.get_weekday_display()].append(label)

        days = [
            {"day": day, "slots": ranges}
            for day, ranges in day_map.items()
        ]

        doctors_availability.append(
            {
                "doctor": doctor,
                "days": days,
            }
        )

    context = {
        "form": form,
        "doctors_availability": doctors_availability,
    }
    return render(request, "scheduling/new_appointment_step1.html", context)


@role_required(User.Roles.PATIENT)
def new_appointment_step2(request):
    """
    Paso 2: el paciente ve los slots disponibles y selecciona uno.
    También escribe el motivo de la consulta.
    """
    doctor_id = request.GET.get("doctor") or request.POST.get("doctor")
    date_str = request.GET.get("date") or request.POST.get("date")

    if not doctor_id or not date_str:
        messages.error(request, "Faltan datos para crear la cita. Vuelve a seleccionar médico y fecha.")
        return redirect("scheduling:new_appointment_step1")

    doctor = get_object_or_404(User, pk=doctor_id, role=User.Roles.DOCTOR)

    try:
        date = datetime.fromisoformat(date_str).date()
    except ValueError:
        messages.error(request, "La fecha seleccionada no es válida.")
        return redirect("scheduling:new_appointment_step1")

    # Calculamos slots disponibles
    slots = get_available_slots_for_doctor_and_date(doctor, date)

    if not slots:
        messages.info(
            request,
            "No hay horarios disponibles para ese médico en la fecha seleccionada. "
            "Elige otra fecha o médico."
        )
        return redirect("scheduling:new_appointment_step1")

    if request.method == "POST":
        form = AppointmentSlotForm(request.POST, slots=slots)
        if form.is_valid():
            slot_value = form.cleaned_data["slot"]
            reason = form.cleaned_data["reason"]

            try:
                slot_start = datetime.fromisoformat(slot_value)
                slot_start = timezone.make_aware(slot_start, timezone.get_current_timezone()) \
                    if timezone.is_naive(slot_start) else slot_start
            except ValueError:
                messages.error(request, "El slot seleccionado no es válido.")
                return redirect("scheduling:new_appointment_step1")

            # Defensa extra: verificar que el slot siga disponible
            latest_slots = get_available_slots_for_doctor_and_date(doctor, date)
            if not any(s[0] == slot_start for s in latest_slots):
                messages.error(
                    request,
                    "El horario seleccionado ya no está disponible. "
                    "Vuelve a seleccionar un horario."
                )
                return redirect(
                    f"{reverse('scheduling:new_appointment_step2')}?doctor={doctor.pk}&date={date.isoformat()}"
                )

            # Crear la cita
            appointment = Appointment.objects.create(
                patient=request.user,
                doctor=doctor,
                scheduled_datetime=slot_start,
                reason=reason,
            )
            messages.success(request, "Cita creada correctamente.")
            return redirect("scheduling:patient_appointments")
    else:
        form = AppointmentSlotForm(slots=slots)

    context = {
        "doctor": doctor,
        "date": date,
        "form": form,
    }
    return render(request, "scheduling/new_appointment_step2.html", context)


@role_required(User.Roles.DOCTOR)
def doctor_appointments(request):
    """
    El médico ve las citas en las que participa como doctor.
    """
    appointments = (
        Appointment.objects
        .filter(doctor=request.user)
        .order_by("-scheduled_datetime")
    )

    context = {
        "appointments": appointments,
    }
    return render(request, "scheduling/doctor_appointments.html", context)


@role_required(User.Roles.PATIENT, User.Roles.DOCTOR, User.Roles.ADMIN)
def cancel_appointment(request, pk):
    """
    Paciente, Médico o Admin pueden cancelar la cita.
    Regla mínima: 
    - Paciente solo cancela si es su cita.
    - Médico solo cancela si es su cita.
    - Admin puede cancelar cualquier cita.
    """
    appointment = get_object_or_404(Appointment, pk=pk)

    user: User = request.user
    # Paciente solo si es su cita
    if user.role == User.Roles.PATIENT and appointment.patient_id != user.id:
        raise PermissionDenied()
    # Médico solo si es su cita
    if user.role == User.Roles.DOCTOR and appointment.doctor_id != user.id:
        raise PermissionDenied()
    # Admin puede siempre

    appointment.cancel()
    messages.success(request, "La cita ha sido cancelada.")
    # Redirigimos según rol
    if user.role == User.Roles.DOCTOR:
        return redirect("scheduling:doctor_appointments")
    elif user.role == User.Roles.PATIENT:
        return redirect("scheduling:patient_appointments")
    else:
        # Admin: por ahora, al home
        return redirect("accounts:home")

@role_required(User.Roles.DOCTOR)
def doctor_availability(request):
    """
    El médico gestiona su disponibilidad semanal.
    """
    availabilities = DoctorAvailability.objects.filter(
        doctor=request.user
    ).order_by("weekday", "start_time")

    if request.method == "POST":
        form = DoctorAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.doctor = request.user
            availability.save()
            messages.success(request, "Disponibilidad guardada correctamente.")
            return redirect("scheduling:doctor_availability")
    else:
        form = DoctorAvailabilityForm()

    context = {
        "availabilities": availabilities,
        "form": form,
    }
    return render(request, "scheduling/doctor_availability.html", context)


@role_required(User.Roles.DOCTOR)
def delete_doctor_availability(request, pk):
    """
    El médico puede eliminar una franja de su propia disponibilidad.
    """
    availability = get_object_or_404(
        DoctorAvailability, pk=pk, doctor=request.user
    )
    availability.delete()
    messages.success(request, "Disponibilidad eliminada.")
    return redirect("scheduling:doctor_availability")
