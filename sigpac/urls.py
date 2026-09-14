from django.urls import path
from . import views

urlpatterns = [
    path("mapa/", views.mapa, name="mapa"),
    path("croquis/", views.croquis_parcela, name="croquis"),
    path("descargar_pdf_parcela/", views.descargar_pdf_parcela, name="descargar_pdf_parcela"),
]