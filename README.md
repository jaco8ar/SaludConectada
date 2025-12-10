# 🏥 SaludConectada – Plataforma de Telemedicina (MVP)

**SaludConectada** es una plataforma de telemedicina construida en **Django 5**, diseñada siguiendo el patrón **MVT** y organizada mediante apps especializadas.  
Soporta tres roles funcionales:

- **Paciente**
- **Médico**
- **Administrador** (rol de negocio, distinto del admin técnico de Django)

Este MVP entrega la funcionalidad principal del sistema: gestión de citas, historial médico, consultas, administración del sistema y un placeholder de videollamada.

---

## 🧩 Características principales

- ✔ Autenticación completa (login, logout, registro de pacientes)  
- ✔ Panel personalizado según rol  
- ✔ Gestión de citas (crear, listar, cancelar)  
- ✔ Historial médico editable por el paciente  
- ✔ Notas de consulta registradas por el médico  
- ✔ Placeholder funcional para videollamada  
- ✔ Panel administrativo con métricas básicas  
- ✔ Gestión de usuarios y roles desde el dashboard admin  
- ✔ Placeholders para supervisión del sistema, reportes y sincronización externa  
- ✔ Admin de Django disponible en ruta independiente para fines técnicos  

---

# 📁 Apps del proyecto

| App | Propósito |
|-----|-----------|
| `accounts` | Autenticación, roles y modelo custom de usuario |
| `scheduling` | Gestión de citas entre pacientes y médicos |
| `clinical` | Historial médico, consultas y notas |
| `dashboard` | Paneles por rol y herramientas administrativas |
| `SaludConectada` | Configuración principal del proyecto |

---

# 👥 Roles del sistema

| Rol | Capacidades |
|-----|-------------|
| **Paciente** | Gestiona citas, historial médico, videollamada (placeholder) |
| **Médico** | Gestiona citas, ve historial del paciente, registra consultas |
| **Administrador** | Métricas, gestión de usuarios, reportes y sincronización |
| **Admin técnico de Django** | Uso interno / desarrollo; no forma parte de los CU |

---

# 🌐 Mapa completo de rutas del sistema

A continuación, todas las rutas disponibles clasificadas por rol.

---

## 🔐 Autenticación y rutas comunes

| Ruta | Descripción |
|------|-------------|
| `/` | Home, redirige según rol |
| `/login/` | Inicio de sesión |
| `/logout/` | Cerrar sesión |
| `/registro/` | Registro de nuevos pacientes |

---

# 👤 Funcionalidades del PACIENTE

## Panel del Paciente
```
/admin/paciente/
```
Incluye:
- Próximas citas
- Última consulta realizada
- Accesos directos:
  - Mis citas
  - Historial médico
  - Videollamada (placeholder)

## Gestión de citas
```
/paciente/citas/
```
Permite:
- Crear citas futuras
- Ver listado de citas propias
- Cancelar citas que aún no están canceladas

## Historial médico
```
/paciente/historial/
```
Edición de:
- Tipo de sangre
- Alergias
- Condiciones crónicas
- Medicamentos
- Notas adicionales

## Videollamada (Placeholder)
```
/citas/<id>/videollamada/
```
- Interfaz simulada de videollamada
- Accesible solo para paciente/médico de la cita

---

# 👨‍⚕️ Funcionalidades del MÉDICO

## Panel del Médico
```
/admin/medico/
```
Incluye:
- Próximas citas asignadas  
- Acciones por cita:
  - Videollamada (placeholder)
  - Ver historial médico del paciente
  - Registrar notas de consulta

## Gestión de citas del médico
```
/medico/citas/
```
- Listado completo de citas donde el usuario es médico
- Cancelación de citas propias

## Historial del paciente (solo viendo)
```
/medico/citas/<id>/historial/

```
- Consulta del historial del paciente asociado a la cita

## Registrar consulta
```
/medico/citas/<id>/consulta/
```
Permite agregar:
- Notas del médico
- Recomendaciones / tratamiento  

La cita se marca como **Completada** al guardar.

---

# 🛠 Funcionalidades del ADMINISTRADOR (rol de negocio)

## Panel administrativo
```
/admin/panel/
```
Incluye:
### Métricas:
- Total de usuarios
- Cantidad por rol
- Total de citas
- Citas por estado

### Herramientas administrativas:
- Gestión de usuarios → `/admin/usuarios/`
- Supervisión (placeholder) → `/admin/sistema/uso/`
- Sincronización externa (placeholder) → `/admin/sistema/sincronizacion-externa/`
- Reportes (placeholder) → `/admin/sistema/reportes/`

## Gestión de usuarios y roles
```
/admin/usuarios/
```
Permite:
- Ver todos los usuarios
- Modificar rol:
  - Paciente
  - Médico
  - Administrador

---

# 🧰 Admin técnico de Django

```
/django-admin/
```

Solo para:
- Tareas internas de desarrollo
- Manipular modelos de bajo nivel
- Crear superusuarios o staff

No forma parte de los casos de uso funcionales del proyecto.

---

# 🧱 Modelo de Usuario

```python
class User(AbstractUser):
    class Roles(models.TextChoices):
        PATIENT = "PATIENT", "Paciente"
        DOCTOR = "DOCTOR", "Médico"
        ADMIN = "ADMIN", "Administrador"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.PATIENT)
```

---

# 🚀 Cómo ejecutar el proyecto localmente

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scriptsctivate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Accesos rápidos:
- Plataforma → http://localhost:8000  
- Admin técnico de Django → http://localhost:8000/django-admin/  
- Panel administrativo → http://localhost:8000/admin/panel/

---

## 🆕 Actualizaciones Recientes (Refinamientos Importantes)

### ✔️ Validaciones y mejoras en Registro
- El correo electrónico ahora es **único en toda la plataforma**.
- El formulario de registro muestra errores por campo y errores generales:
  - Usuario ya existente
  - Correo ya registrado
  - Contraseñas que no coinciden
- Los valores de los campos se conservan al fallar el registro (excepto contraseñas).

### ✔️ Validaciones y mejoras en Login
- Se muestran mensajes claros cuando:
  - Las credenciales no son correctas
  - La cuenta está inactiva o bloqueada
  - Falta llenar un campo obligatorio
- El campo de usuario conserva su valor si el login falla.

---

## ⏰ Sistema de Disponibilidad Médica y Agenda por "Slots"

El sistema ahora usa un modelo más realista y robusto para gestionar horarios médicos y evitar solapamientos.

### ✔️ Duración fija de cada cita: **20 minutos**

### ✔️ Los pacientes seleccionan un *slot* definido, no una hora libre al azar
Ejemplo:
- `08:00 – 08:20`
- `08:20 – 08:40`
- `08:40 – 09:00`

### ✔️ Generación automática de slots por día según disponibilidad del médico
Los médicos configuran:
- Día de la semana  
- Hora de inicio  
- Hora de fin  

El sistema crea bloques consecutivos de 20 minutos.

### ✔️ Reglas estrictas contra solapamientos
- Un paciente no puede tomar un slot ya ocupado.
- Dos citas no pueden ocurrir al mismo tiempo para el mismo médico.
- Se valida que los horarios estén dentro de la disponibilidad real del médico.

### ✔️ Visualización inteligente
Al crear una cita:
- El paciente elige médico y fecha.
- El sistema muestra **solo los slots disponibles reales**.
- El usuario puede retroceder sin perder los datos ya seleccionados.

---

## 🔐 Reglas adicionales para Gestión de Roles (Admin)

### ✔️ 1. No permitir que un admin se cambie su propio rol
Prevención de pérdida accidental de privilegios.

### ✔️ 2. No permitir cambiar el rol de un médico si tiene citas futuras activas
Un médico no puede convertirse en paciente o admin si:
- Tiene citas programadas a futuro
- Dichas citas no están canceladas

### ✔️ 3. Un usuario convertido a médico debe tener disponibilidad mínima
Si un admin convierte un usuario a médico:
- Se crea automáticamente disponibilidad básica (L–V, 08:00–12:00)
- El médico podrá ajustarla luego

---

## 👥 Usuarios de prueba disponibles

Puedes usar estas cuentas para navegar el sistema según cada rol:

### 🔸 Administrador
- **Usuario:** `pipe`  
- **Contraseña:** `123`

### 🔸 Médico
- **Usuario:** `medico1`  
- **Contraseña:** `Doctor2025`

### 🔸 Paciente
- **Usuario:** `carlosdiaz`  
- **Contraseña:** `Testing2025`

---



