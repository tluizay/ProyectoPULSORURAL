import logging
from django.http import JsonResponse
from .solgrids_services import PropiedadesHidricas  

logger = logging.getLogger(__name__)

def api_diagnostico_aguas(request):
   
    lat_param = request.GET.get("lat")
    lon_param = request.GET.get("lon")

    if not lat_param or not lon_param:
        return JsonResponse({"error": "Faltan las coordenadas lat y lon"}, status=400)

    try:
        lat = float(lat_param.replace(",", "."))
        lon = float(lon_param.replace(",", "."))
    except ValueError:
        return JsonResponse({"error": "Coordenadas no válidas"}, status=400)

    try:
        servicio_hidrico = PropiedadesHidricas()
        datos_brutos = servicio_hidrico.fetch(lat, lon)
        

        resultado_normalizado = servicio_hidrico.normalize(datos_brutos)

        return JsonResponse(resultado_normalizado)
    except Exception as e:
        logger.error("Error al procesar el diagnóstico hídrico: %s", e)
        return JsonResponse({"error": str(e)}, status=500)