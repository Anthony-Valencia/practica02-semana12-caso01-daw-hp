# prestamos/admin.py
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Equipo, Prestamo, Laboratorio


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_patrimonial', 'nombre', 'marca', 'categoria',
        'estado_coloreado', 'laboratorio', 'dias_desde_mantenimiento',
    ]
    list_filter = ['laboratorio', 'estado', 'categoria']
    search_fields = ['codigo_patrimonial', 'nombre', 'categoria']
    actions = ['marcar_en_mantenimiento']

    @admin.display(description='Estado')
    def estado_coloreado(self, obj):
        colores = {
            'operativo': 'green',
            'mantenimiento': 'orange',
            'baja': 'red',
        }
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            colores.get(obj.estado, 'black'),
            obj.get_estado_display(),
        )

    @admin.action(description='Marcar como en mantenimiento')
    def marcar_en_mantenimiento(self, request, queryset):
        actualizados = queryset.update(estado='mantenimiento')
        self.message_user(request, f'{actualizados} equipos marcados en mantenimiento.')


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'docente', 'equipo', 'fecha_prestamo',
        'fecha_devolucion_esperada', 'estado', 'dias_retraso',
    ]
    list_filter = ['estado', 'fecha_prestamo', 'fecha_devolucion_esperada', 'docente']
    search_fields = ['equipo__codigo_patrimonial', 'docente__username', 'docente__first_name']
    actions = ['enviar_recordatorio']

    @admin.display(description='Días de retraso')
    def dias_retraso(self, obj):
        return obj.dias_retraso()

    @admin.action(description='Enviar recordatorio de devolución')
    def enviar_recordatorio(self, request, queryset):
        vencidos = queryset.filter(estado='activo', fecha_devolucion_esperada__lt=timezone.now().date())
        self.message_user(
            request,
            f'Recordatorio simulado enviado a {vencidos.count()} préstamos vencidos.'
        )