# scheduling/services.py
import requests
from django.conf import settings
from django.utils.crypto import get_random_string
from datetime import timedelta

DAILY_ROOMS_ENDPOINT = f"{settings.DAILY_API_BASE_URL}/rooms"


def create_daily_room_for_appointment(appointment):
    """
    Crea una sala Daily para una cita concreta y devuelve la URL.

    Usa la API REST de Daily:
    POST /rooms
    """
    if not settings.DAILY_API_KEY or not settings.DAILY_DOMAIN:
        # Si no está configurado, devolvemos None para no romper el flujo
        return None

    # Nombre único de sala (no tiene por qué ser secreto, pero sí único)
    room_name = f"cita-{appointment.pk}-{get_random_string(8)}"

    # Opcional: caducidad de la sala un tiempo después de la cita.
    # Ejemplo: 2 horas después de la hora programada.
    exp_timestamp = int(
        (appointment.scheduled_datetime + timedelta(hours=2)).timestamp()
    )

    payload = {
        "name": room_name,
        "privacy": "private",  # solo con URL / tokens
        "properties": {
            "exp": exp_timestamp,
        },
    }

    headers = {
        "Authorization": f"Bearer {settings.DAILY_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(DAILY_ROOMS_ENDPOINT, json=payload, headers=headers)

    if response.status_code not in (200, 201):
        # Podrías loguear el error aquí
        return None

    data = response.json()
    # La respuesta incluye un campo `url` tipo https://<domain>.daily.co/<room-name>/ :contentReference[oaicite:6]{index=6}
    return data.get("url")
