from django.urls import path
from . import views

urlpatterns = [
    path('', views.tsm_checker_view, name='tsm_home'),
]