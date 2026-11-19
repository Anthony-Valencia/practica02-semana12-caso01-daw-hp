# prestamos/urls.py
from django.urls import path
from . import views

app_name = 'prestamos'

urlpatterns = [
    path('', views.lista_prestamos, name='lista'),
    path('crear/', views.crear_prestamo, name='crear'),
    path('devolver/<int:pk>/', views.registrar_devolucion, name='devolver'),
]