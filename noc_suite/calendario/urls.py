from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendario_view, name='calendario_home'),
    path('api/eventos/', views.api_eventos, name='api_eventos'),
    path('api/guardar/', views.api_guardar_evento, name='api_guardar'),
    path('api/eliminar/', views.api_eliminar_evento, name='api_eliminar'),
]