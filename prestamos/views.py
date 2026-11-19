# prestamos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from .models import Equipo, Prestamo
from .forms import PrestamoForm, DevolucionForm


@login_required
def lista_prestamos(request):
    """Docentes solo ven sus propios préstamos; admin/asistente ven todos."""
    if request.user.groups.filter(name='Docente').exists():
        prestamos = Prestamo.objects.filter(docente=request.user).select_related('equipo', 'docente')
    else:
        prestamos = Prestamo.objects.all().select_related('equipo', 'docente')
    return render(request, 'prestamos/lista.html', {'prestamos': prestamos})


@login_required
def crear_prestamo(request):
    """Cualquier usuario autenticado puede solicitar (docente) o registrar (asistente)."""
    if request.method == 'POST':
        form = PrestamoForm(request.POST)
        if form.is_valid():
            prestamo = form.save(commit=False)
            prestamo.registrado_por = request.user
            prestamo.save()
            messages.success(request, 'Préstamo registrado correctamente.')
            return redirect('prestamos:lista')
    else:
        form = PrestamoForm()
    return render(request, 'prestamos/form.html', {'form': form, 'titulo': 'Nuevo Préstamo'})


@login_required
@permission_required('prestamos.change_prestamo', raise_exception=True)
def registrar_devolucion(request, pk):
    """Solo asistentes (con permiso) pueden registrar devoluciones (RF3)."""
    prestamo = get_object_or_404(Prestamo, pk=pk)
    if request.method == 'POST':
        form = DevolucionForm(request.POST, instance=prestamo)
        if form.is_valid():
            prestamo = form.save(commit=False)
            prestamo.estado = 'devuelto'
            prestamo.save()
            messages.success(request, 'Devolución registrada.')
            return redirect('prestamos:lista')
    else:
        form = DevolucionForm(instance=prestamo)
    return render(request, 'prestamos/form.html', {'form': form, 'titulo': 'Registrar Devolución'})