from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.tsm_monitor_dashboard, name='tsm_monitor_dashboard'),
]