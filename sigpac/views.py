import json
from django.shortcuts import render
from django.http import HttpResponseBadRequest
from .service import SigpacPuntoService
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

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

@login_required
def descargar_pdf_parcela(request):
    if request.method == 'POST':
        try:
            # 1. Recibimos el JSON enviado por JavaScript desde el cliente
            data = json.loads(request.body)
            
            lat = data.get('lat', '42.5987')
            lon = data.get('lon', '-5.5671')
            datos_recinto = data.get('datos_recinto', {})
            clima_aemet = data.get('clima_aemet', {})
            datos_hidricos = data.get('datos_hidricos', {})
            datos_suelo = data.get('datos_suelo', {})

            # 2. Pasamos toda la información estructurada al contexto de la plantilla
            contexto = {
                'latitud': lat,
                'longitud': lon,
                'datos_recinto': datos_recinto,
                'clima_aemet': clima_aemet,
                'datos_hidricos': datos_hidricos,
                'datos_suelo': datos_suelo,
            }

            # 3. Renderizamos la plantilla HTML estática para PDF
            template = get_template('sigpac/descargar_pdf_parcela.html')
            html = template.render(contexto, request)

            # 4. Generamos la respuesta en formato PDF binario
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Informe_Completo_Parcela.pdf"'
            
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return HttpResponse('Error al generar el PDF', status=500)
            
            return response

        except Exception as e:
            print(f"Error procesando PDF por JS: {e}")
            return HttpResponse(f"Error interno: {e}", status=500)
            
    return HttpResponse("Método no permitido", status=405)