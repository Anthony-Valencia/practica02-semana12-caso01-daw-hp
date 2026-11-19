# prestamos/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone


class Laboratorio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.nombre


class Equipo(models.Model):
    ESTADO_CHOICES = [
        ('operativo', 'Operativo'),
        ('mantenimiento', 'En mantenimiento'),
        ('baja', 'Dado de baja'),
    ]

    codigo_patrimonial = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='operativo')
    laboratorio = models.ForeignKey(
        Laboratorio, on_delete=models.PROTECT, related_name='equipos'
    )
    ultimo_mantenimiento = models.DateField(null=True, blank=True)
    stock_total = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def dias_desde_mantenimiento(self):
        if not self.ultimo_mantenimiento:
            return None
        return (timezone.now().date() - self.ultimo_mantenimiento).days

    def __str__(self):
        return f"{self.codigo_patrimonial} - {self.nombre}"

class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('devuelto', 'Devuelto'),
        ('vencido', 'Vencido'),
    ]

    docente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prestamos',
        limit_choices_to={'groups__name': 'Docente'},
    )
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='prestamos')
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    fecha_prestamo = models.DateField()
    fecha_devolucion_esperada = models.DateField()
    fecha_devolucion_real = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    observaciones = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='prestamos_registrados',
    )

    def dias_retraso(self):
        if self.estado == 'devuelto' or not self.fecha_devolucion_esperada:
            return 0
        hoy = timezone.now().date()
        delta = hoy - self.fecha_devolucion_esperada
        return max(delta.days, 0)

    def __str__(self):
        return f"Préstamo #{self.pk} - {self.docente} - {self.equipo}"