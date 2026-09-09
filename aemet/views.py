from datetime import datetime
from django.http import JsonResponse
from aemet.agregador import ClimaInteligenteAggregator


def api_diagnostico_clima(request):
    try:
        anio = int(request.GET.get('anio', datetime.now().year))
        mes = int(request.GET.get('mes', datetime.now().month))
        lat = float(request.GET.get('lat', 0.0))
        lon = float(request.GET.get('lon', 0.0))
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Los parámetros anio, mes, lat y lon deben ser numéricos.'}, status=400)
    
    forzar_regeneracion = request.GET.get('regenerar') == '1'
    estacion = request.GET.get('estacion')
   
    # Llamamos al agregador pasando todos los filtros necesarios
    resultado = ClimaInteligenteAggregator.obtener_analisis_completo(
        identificador_estacion=estacion, 
        latitud=lat, 
        longitud=lon,
        anio=anio,
        mes=mes,
        forzar_regeneracion=forzar_regeneracion
    )
    
    return JsonResponse(resultado, safe=False)
