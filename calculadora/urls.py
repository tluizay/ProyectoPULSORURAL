from django.urls import path
from . import views

urlpatterns = [
    path("asistente_calcularoas/", views.asistente_calculadora, name="asistente_calculadora"),
    path("calculadora/", views.calcular, name="calculadora"),
]