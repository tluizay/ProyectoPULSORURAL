from django.http import JsonResponse
from itacyl.itacyl_services import Suelos
from itacyl.gemini_services import asistente_virtual  

def api_diagnostico_suelo(request):
    try:
        lat = float(request.GET.get('lat', 0.0))
        lon = float(request.GET.get('lon', 0.0))
    except (ValueError, TypeError):
        return JsonResponse({"error": "Parámetros 'lat' y 'lon' inválidos."}, status=400)

    servicio_suelos = Suelos()
    datos_suelo = servicio_suelos.get_data(lat=lat, lng=lon)

    if "error" in datos_suelo:
        return JsonResponse(datos_suelo, status=500)

    interpretacion = asistente_virtual(contexto_negocio=datos_suelo)

    resultado_final = {
        **datos_suelo,
        **interpretacion
    }

    return JsonResponse(resultado_final, safe=False)
