from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from decouple import config

urlpatterns = [
    # AGREGAMOS name='home' AL FINAL DE ESTA LÍNEA
    path(config('ADMIN_URL', default='admin/'), admin.site.urls),
    path('', RedirectView.as_view(url='/usuarios/dashboard/', permanent=False), name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('usuarios/', include('csv_validator.urls')),
    path('calendario/', include('calendario.urls')),
    path('tsm/', include('tsm_checker.urls')),
    path('tsm-monitor/', include('tsm_monitor.urls')),
    path('admin-panel/', include('core_admin.urls')),
    path('iso8583/', include('iso8583_parser.urls')),
]