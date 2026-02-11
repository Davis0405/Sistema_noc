from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('action/<str:action>/', views.service_action, name='service_action'),
]