from django.urls import path
from . import views


urlpatterns = [
    path("rendimientos/", views.vista_evolucion_agraria, name="rendimientos"),
    
]