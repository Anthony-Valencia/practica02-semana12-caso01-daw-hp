# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView # <-- Importamos esto

urlpatterns = [
    # Añadimos esta línea para la ruta raíz:
    path('', RedirectView.as_view(pattern_name='prestamos:lista', permanent=False)),
    
    path('admin/', admin.site.urls),
    path('prestamos/', include('prestamos.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]