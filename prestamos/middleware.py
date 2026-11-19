# prestamos/middleware.py
import logging
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger('auditoria')


class AuditoriaMiddleware:
    """Registra acciones críticas: préstamo, devolución, eliminación (RF4)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and request.method == 'POST':
            # Solo rutas de interés
            rutas_criticas = ['/prestamos/crear/', '/prestamos/devolver/']
            if any(request.path.startswith(r) for r in rutas_criticas):
                ip = request.META.get('REMOTE_ADDR', 'desconocida')
                logger.info(
                    f"AUDITORÍA | Usuario: {request.user.username} | "
                    f"IP: {ip} | Ruta: {request.path} | "
                    f"Hora: {timezone.now().isoformat()}"
                )
        return response


class PrestamosVencidosMiddleware:
    """Al iniciar sesión, muestra alerta si el usuario tiene préstamos vencidos."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.session.get('alerta_vencidos_mostrada'):
            from .models import Prestamo
            vencidos = Prestamo.objects.filter(
                docente=request.user,
                estado='activo',
                fecha_devolucion_esperada__lt=timezone.now().date(),
            ).count()
            if vencidos:
                messages.warning(
                    request,
                    f"Tienes {vencidos} préstamo(s) vencido(s). Por favor, regulariza la devolución."
                )
            request.session['alerta_vencidos_mostrada'] = True
        return self.get_response(request)


class SessionInactivityMiddleware:
    """Cierra la sesión tras 30 minutos de inactividad (RF3)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            ahora = timezone.now().timestamp()
            ultimo = request.session.get('ultima_actividad')
            if ultimo and (ahora - ultimo) > 1800:  # 30 minutos
                from django.contrib.auth import logout
                logout(request)
                return redirect(reverse('login') + '?sesion_expirada=1')
            request.session['ultima_actividad'] = ahora
        return self.get_response(request)