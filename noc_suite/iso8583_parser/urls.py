from django.urls import path
from . import views

urlpatterns = [
    path('individual/', views.parser_individual, name='iso_individual'),
    path('masivo/', views.parser_masivo, name='iso_masivo'),
]