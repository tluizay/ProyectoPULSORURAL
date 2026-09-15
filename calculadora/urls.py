from django.urls import path
from . import views

urlpatterns = [
    path("asistente_calcularoas/", views.asistente_calculadora, name="asistente_calculadora"),
    path("calculadora/", views.calcular, name="calculadora"),
    path("grafica_comparativa/",views.calcular_grafica_comparativa,name="grafica_comparativa"),
]