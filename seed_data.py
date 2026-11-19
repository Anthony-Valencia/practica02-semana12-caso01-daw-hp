# seed_data.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from prestamos.models import Laboratorio, Equipo, Prestamo
from datetime import date, timedelta

Usuario = get_user_model()

# Grupos
admin_group, _ = Group.objects.get_or_create(name='Administrador')
docente_group, _ = Group.objects.get_or_create(name='Docente')
asistente_group, _ = Group.objects.get_or_create(name='Asistente')

# Permisos para asistente (cambiar préstamo)
perm_change = Permission.objects.get(codename='change_prestamo')
asistente_group.permissions.add(perm_change)

# Usuarios
admin_user, _ = Usuario.objects.get_or_create(
    username='admin', defaults={'email': 'admin@uncp.edu.pe', 'first_name': 'Admin', 'last_name': 'Lab', 'is_staff': True, 'is_superuser': True}
)
docente1, _ = Usuario.objects.get_or_create(
    username='docente1', defaults={'email': 'docente1@uncp.edu.pe', 'first_name': 'Juan', 'last_name': 'Pérez', 'codigo_uncp': 'D001'}
)
docente2, _ = Usuario.objects.get_or_create(
    username='docente2', defaults={'email': 'docente2@uncp.edu.pe', 'first_name': 'María', 'last_name': 'López', 'codigo_uncp': 'D002'}
)
asistente1, _ = Usuario.objects.get_or_create(
    username='asistente1', defaults={'email': 'asistente1@uncp.edu.pe', 'first_name': 'Carlos', 'last_name': 'Ruiz'}
)

docente_group.user_set.add(docente1, docente2)
asistente_group.user_set.add(asistente1)

# Laboratorios
lab1, _ = Laboratorio.objects.get_or_create(nombre='Lab Sistemas 1', ubicacion='Pabellón A')
lab2, _ = Laboratorio.objects.get_or_create(nombre='Lab Redes', ubicacion='Pabellón B')

# Equipos (10)
equipos_data = [
    ('LAP-001', 'Laptop HP', 'HP', 'ProBook 450', 'Laptop', 'operativo', lab1, 5),
    ('LAP-002', 'Laptop Dell', 'Dell', 'Latitude 5420', 'Laptop', 'operativo', lab1, 10),
    ('PROY-001', 'Proyector Epson', 'Epson', 'PowerLite X49', 'Proyector', 'operativo', lab1, 3),
    ('CAM-001', 'Cámara Canon', 'Canon', 'EOS Rebel T7', 'Cámara', 'operativo', lab2, 7),
    ('ARD-001', 'Kit Arduino Uno', 'Arduino', 'R3', 'Kit', 'operativo', lab1, 2),
    ('ROUT-001', 'Router Cisco', 'Cisco', 'RV340', 'Router', 'operativo', lab2, 4),
    ('SW-001', 'Switch TP-Link', 'TP-Link', 'TL-SG1024', 'Switch', 'mantenimiento', lab2, 1),
    ('LAP-003', 'Laptop Lenovo', 'Lenovo', 'ThinkPad E14', 'Laptop', 'operativo', lab1, 6),
    ('PROY-002', 'Proyector BenQ', 'BenQ', 'MS550', 'Proyector', 'baja', lab2, None),
    ('CAM-002', 'Cámara Nikon', 'Nikon', 'D3500', 'Cámara', 'operativo', lab1, 8),
]

for cod, nom, marca, modelo, cat, est, lab, dias in equipos_data:
    ult = date.today() - timedelta(days=dias) if dias else None
    Equipo.objects.get_or_create(
        codigo_patrimonial=cod,
        defaults={
            'nombre': nom, 'marca': marca, 'modelo': modelo,
            'categoria': cat, 'estado': est, 'laboratorio': lab,
            'ultimo_mantenimiento': ult, 'stock_total': 3 if 'LAP' in cod else 1,
        }
    )

# Préstamos (15)
equipos = list(Equipo.objects.filter(estado='operativo')[:5])
hoy = date.today()
for i in range(15):
    eq = equipos[i % len(equipos)]
    doc = docente1 if i % 2 == 0 else docente2
    Prestamo.objects.get_or_create(
        docente=doc, equipo=eq, cantidad=1,
        defaults={
            'fecha_prestamo': hoy - timedelta(days=i+1),
            'fecha_devolucion_esperada': hoy + timedelta(days=5 - i),
            'estado': 'activo' if i < 10 else 'devuelto',
            'fecha_devolucion_real': hoy - timedelta(days=1) if i >= 10 else None,
            'registrado_por': asistente1,
        }
    )

print("Datos de prueba creados correctamente.")