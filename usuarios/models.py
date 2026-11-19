# usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuario personalizado con roles simulados mediante Groups."""
    codigo_uncp = models.CharField(
        max_length=20, blank=True,
        help_text="Código institucional UNCP (solo docentes/estudiantes)"
    )
    telefono = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"