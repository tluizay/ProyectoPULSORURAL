from django.urls import path
from . import views

app_name = 'itacyl'

urlpatterns = [
    path("consulta_suelos/", views.api_diagnostico_suelo, name="consulta_suelo"),
    
]