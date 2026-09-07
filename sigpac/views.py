import json
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from .service import SigpacPuntoService
from aemet.aemet_services import Aemet



def mapa(request):
    return render(request, "sigpac/mapa.html")

def croquis_parcela(peticion_http):
    latitud_parametro = peticion_http.GET.get("lat")
    longitud_parametro = peticion_http.GET.get("lon") or peticion_http.GET.get("lng")

    if not latitud_parametro or not longitud_parametro:
        return HttpResponseBadRequest("Faltan las coordenadas")

    try:
        latitud = float(latitud_parametro)
        longitud = float(longitud_parametro)
    except ValueError:
        return HttpResponseBadRequest("Coordenadas no válidas")

    # 1. Solo SIGPAC (rápido, 2-5s)
    servicio_sigpac = SigpacPuntoService()
    datos_recinto = servicio_sigpac.get_data(latitud, longitud)

    geometria_json = None
    if datos_recinto and datos_recinto.get("geometria"):
        geometria_json = json.dumps(datos_recinto["geometria"])

   
    return render(
        peticion_http,
        "sigpac/mapa.html",
        {
            "datos_recinto": datos_recinto,
            "geometria_json": geometria_json,
            "latitud": latitud,
            "longitud": longitud,
        },
    )   