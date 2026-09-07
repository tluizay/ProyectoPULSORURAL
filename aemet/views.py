from django.http import JsonResponse
from aemet.agregador import ClimaInteligenteAggregator

def api_diagnostico_clima(request):
    estacion = request.GET.get('estacion')
    lat = float(request.GET.get('lat', 0.0))
    lon = float(request.GET.get('lon', 0.0))
    
    # El agregador se encarga de todo el trabajo pesado por debajo
    resultado = ClimaInteligenteAggregator.obtener_analisis_completo(
        identificador_estacion=estacion, 
        latitud=lat, 
        longitud=lon
    )
    
    return JsonResponse(resultado, safe=False)
