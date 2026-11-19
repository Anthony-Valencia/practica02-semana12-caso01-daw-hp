# Sistema de Gestión de Préstamos de Equipos de Laboratorio - UNCP

Aplicación web desarrollada con Django 5.2 LTS para digitalizar el préstamo de equipos de los laboratorios de la Facultad de Ingeniería de Sistemas.

## Características

- Gestión de equipos con estados (operativo/mantenimiento/baja) y colores en Admin.
- Formulario de préstamo con validaciones cruzadas: stock, estado del equipo, límite de 3 préstamos activos por docente.
- Devoluciones registradas solo por asistentes (permisos).
- Middleware de auditoría (logs en consola), alerta de préstamos vencidos y cierre de sesión por inactividad (30 min).
- Sesiones HttpOnly y CSRF en todos los formularios.
- Admin personalizado: filtros, búsquedas y acciones masivas.

## Requisitos

- Python 3.10+
- Django 5.2
- django-crispy-forms 2.6
- crispy-bootstrap5 2026.3

## Instalación

1. Clona el repositorio:
   ```bash
   git clone <URL_DEL_REPO>
   cd <REPO>