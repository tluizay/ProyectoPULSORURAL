from django.shortcuts import render
from ine.agregador import IneAgregador
from django.http import JsonResponse
from datetime import datetime

def vista_evolucion_agraria(request):
    cache_key = 'informe_unificado_global'
    forzar = request.GET.get('regenerar') == '1'

    # 1. Obtener de sesión o invocar al agregador unificado
    if not forzar and cache_key in request.session:
        resultado = request.session[cache_key]
    else:
        # Llamamos al único método que ahora hace todo
        resultado = IneAgregador.obtener_todo_unificado("panel_completo")
        print("RESULTADO INE AGREGADOR:", resultado.get("estado"))
        
        if resultado.get('estado') == 'ok':
            request.session[cache_key] = resultado

    # 2. Responder si es una petición AJAX (fetch desde javascript)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        status_code = 200 if resultado.get('estado') == 'ok' else 400
        return JsonResponse(resultado, status=status_code)

    # 3. Control de errores
    if resultado.get("estado") == "error":
        return render(request, "ine/rendimientos.html", {"mensaje_error": resultado.get("mensaje")})

    # 4. Extraer los datos de la gráfica
    datos = resultado.get("datos_grafica", {})

    # 5. Construir el contexto unificado
    contexto = {
        # Datos para Chart.js
        "datos_evolucion": datos,       # Contiene 'vegetal' y 'animal'
        "datos_provinciales": datos,    # Contiene 'evolucion_global' y 'provincial_anio'
        
        # Datos para el HTML y Gemini
        "analisis_md": resultado.get('informe_ia'),
        "informe_principal": resultado.get('datos'),
        "todos_los_informes": resultado.get('panel_completo', []), # <-- Ojo aquí, usamos la clave de tu nuevo agregador
        "mensaje_error": None,
    }

    # 6. Renderizar una única plantilla con toda la información
    return render(request, "ine/rendimientos.html", contexto)