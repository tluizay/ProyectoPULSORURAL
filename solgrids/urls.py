from django.urls import path
from . import views

urlpatterns = [
   
    path("consulta_aguas/", views.api_diagnostico_aguas, name="consulta_aguas"),
]