# prestamos/forms.py
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Prestamo, Equipo


class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = [
            'docente', 'equipo', 'cantidad',
            'fecha_prestamo', 'fecha_devolucion_esperada', 'observaciones',
        ]
        widgets = {
            'fecha_prestamo': forms.DateInput(attrs={'type': 'date'}),
            'fecha_devolucion_esperada': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_fecha_devolucion_esperada(self):
        """La fecha de devolución debe ser posterior a la de préstamo (RF2)."""
        fecha_dev = self.cleaned_data.get('fecha_devolucion_esperada')
        fecha_prest = self.cleaned_data.get('fecha_prestamo')
        if fecha_dev and fecha_prest and fecha_dev <= fecha_prest:
            raise ValidationError(
                "La fecha de devolución debe ser posterior a la fecha de préstamo."
            )
        return fecha_dev

    def clean(self):
        """Validaciones cruzadas: stock, estado del equipo, límite de préstamos."""
        cleaned = super().clean()
        equipo = cleaned.get('equipo')
        cantidad = cleaned.get('cantidad')
        docente = cleaned.get('docente')

        # Equipo operativo
        if equipo and equipo.estado != 'operativo':
            raise ValidationError(
                f"El equipo '{equipo.nombre}' no está operativo (estado: {equipo.get_estado_display()})."
            )

        # Stock disponible vs cantidad solicitada
        if equipo and cantidad:
            prestados = Prestamo.objects.filter(
                equipo=equipo, estado='activo'
            ).aggregate(total=models.Sum('cantidad'))['total'] or 0
            disponible = equipo.stock_total - prestados
            if cantidad > disponible:
                raise ValidationError(
                    f"Stock insuficiente. Disponible: {disponible}, solicitado: {cantidad}."
                )

        # Docente no puede tener más de 3 préstamos activos
        if docente:
            activos = Prestamo.objects.filter(docente=docente, estado='activo').count()
            if activos >= 3:
                raise ValidationError(
                    "El docente ya tiene 3 préstamos activos (límite máximo)."
                )

        # Sanitización básica de observaciones
        obs = cleaned.get('observaciones', '')
        if obs and '<script>' in obs.lower():
            raise ValidationError("Las observaciones contienen contenido no permitido.")

        return cleaned

class DevolucionForm(forms.ModelForm):
    """Solo asistentes pueden registrar devoluciones (RF3)."""
    estado_equipo_al_retornar = forms.ChoiceField(
        choices=Equipo.ESTADO_CHOICES,
        label="Estado del equipo al retornar",
    )

    class Meta:
        model = Prestamo
        fields = ['fecha_devolucion_real', 'observaciones']
        widgets = {
            'fecha_devolucion_real': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_fecha_devolucion_real(self):
        fecha = self.cleaned_data.get('fecha_devolucion_real')
        if fecha and fecha > timezone.now().date():
            raise ValidationError("La fecha de devolución no puede ser futura.")
        return fecha