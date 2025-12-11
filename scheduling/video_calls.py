# scheduling/video_calls.py
import requests
from datetime import timedelta
from django.conf import settings


DAILY_API_BASE_URL = getattr(settings, "DAILY_API_BASE_URL", "https://api.daily.co/v1")
DAILY_API_KEY = getattr(settings, "DAILY_API_KEY", "")
DAILY_ROOMS_ENDPOINT = f"{DAILY_API_BASE_URL}/rooms"


def create_daily_room_for_appointment(appointment):
    """
    Crea una sala Daily para una cita concreta y devuelve la URL.

    IMPORTANTE: este módulo NO importa models para evitar ciclos.
    Recibe la instancia de Appointment como parámetro.
    """
    if not DAILY_API_KEY or not getattr(settings, "DAILY_DOMAIN", ""):
        # Si no está configurado, devolvemos None para no romper el flujo
        return None

    from django.utils.crypto import get_random_string  # import local para evitar dependencias globales

    room_name = f"cita-{appointment.pk}-{get_random_string(8)}"

    # Ejemplo: sala expira 2h después de la cita
    exp_timestamp = int(
        (appointment.scheduled_datetime + timedelta(hours=2)).timestamp()
    )

    payload = {
        "name": room_name,
        "privacy": "public", 
        "properties": {
            "exp": exp_timestamp,
        },
}

    headers = {
        "Authorization": f"Bearer {DAILY_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(DAILY_ROOMS_ENDPOINT, json=payload, headers=headers)

    if response.status_code not in (200, 201):
        # TODO: loguear el error si quieres
        return None

    data = response.json()
    return data.get("url")
