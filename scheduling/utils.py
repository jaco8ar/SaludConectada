from datetime import datetime, time

from django.utils import timezone

from .models import Appointment, DoctorAvailability, APPOINTMENT_SLOT_DELTA


def _make_aware(dt: datetime) -> datetime:
    """
    Convierte un datetime naïve a timezone-aware usando la zona por defecto.
    Si ya es aware, lo devuelve igual.
    """
    if timezone.is_aware(dt):
        return dt
    return timezone.make_aware(dt, timezone.get_current_timezone())


def get_available_slots_for_doctor_and_date(doctor, date):
    """
    Devuelve una lista de tuplas (slot_start, slot_end) para un doctor y una fecha concreta,
    respetando:
    - Disponibilidad configurada (DoctorAvailability)
    - Citas ya asignadas (evita solapamientos)
    - No generar slots en el pasado si la fecha es hoy
    Cada slot dura APPOINTMENT_SLOT_DELTA (20 minutos).
    """
    weekday = date.weekday()

    # 1. Disponibilidad activa del doctor en ese día de la semana
    availabilities = DoctorAvailability.objects.filter(
        doctor=doctor,
        is_active=True,
        weekday=weekday,
    )

    if not availabilities.exists():
        return []

    tz = timezone.get_current_timezone()

    # 2. Citas existentes del doctor ese día
    day_start = _make_aware(datetime.combine(date, time.min))
    day_end = _make_aware(datetime.combine(date, time.max))

    existing_appointments = Appointment.objects.filter(
        doctor=doctor,
        scheduled_datetime__gte=day_start,
        scheduled_datetime__lte=day_end,
    ).exclude(status=Appointment.Status.CANCELED)

    occupied_intervals = [
        (
            appt.scheduled_datetime,
            appt.scheduled_datetime + APPOINTMENT_SLOT_DELTA,
        )
        for appt in existing_appointments
    ]

    # 3. Generar slots por cada franja de disponibilidad
    slots = []
    now = timezone.now()

    for avail in availabilities:
        current_start = _make_aware(datetime.combine(date, avail.start_time))
        avail_end = _make_aware(datetime.combine(date, avail.end_time))

        # Si es hoy, evitamos slots totalmente en el pasado
        if date == now.date() and current_start < now:
            while current_start < now:
                current_start += APPOINTMENT_SLOT_DELTA

        # Generamos slots [start, start+20) dentro de la franja
        while current_start + APPOINTMENT_SLOT_DELTA <= avail_end:
            slot_start = current_start
            slot_end = current_start + APPOINTMENT_SLOT_DELTA

            # Comprobar solapamiento con citas existentes
            has_conflict = any(
                not (slot_end <= occ_start or slot_start >= occ_end)
                for occ_start, occ_end in occupied_intervals
            )

            if not has_conflict:
                slots.append((slot_start, slot_end))

            current_start += APPOINTMENT_SLOT_DELTA

    # Ordenamos por inicio de slot
    slots.sort(key=lambda s: s[0])
    return slots
