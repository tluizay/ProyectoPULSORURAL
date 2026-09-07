from django.urls import path
from . import views

app_name = 'aemet'

urlpatterns = [
    path("consulta_clima/", views.api_diagnostico_clima, name="consulta_clima"),
    
]