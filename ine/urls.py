from django.urls import path
from . import views


urlpatterns = [
    path("rendimientos/", views.vista_evolucion_agraria, name="rendimientos"),
    path("rendimientos/descargar-pdf/", views.descargar_pdf, name="pdf_rendimientos"),
    
]