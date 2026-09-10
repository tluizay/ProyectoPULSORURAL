from django.shortcuts import render
from ine.agregador import IneAgregador
from django.http import JsonResponse
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
import matplotlib
matplotlib.use("Agg")  # backend sin GUI, necesario en servidor
import matplotlib.pyplot as plt
import io, base64

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


def generar_imagen_barras(datos_grafica: dict, titulo: str) -> str:
    fig, ax = plt.subplots(figsize=(6, 3))
    for dataset in datos_grafica.get("datasets", []):
        ax.bar(datos_grafica["labels"], dataset["data"], label=dataset.get("label"))
    ax.set_title(titulo)
    ax.legend(fontsize=7)
    plt.xticks(rotation=45, fontsize=7)
    plt.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=120)
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")

def generar_imagen_torta(datos_grafica: dict, titulo: str) -> str:
    fig, ax = plt.subplots(figsize=(4, 4))
    dataset = datos_grafica.get("datasets", [{}])[0]
    ax.pie(
        dataset.get("data", []),
        labels=datos_grafica.get("labels", []),
        colors=dataset.get("backgroundColor"),
        autopct="%1.1f%%",
        textprops={"fontsize": 7}
    )
    ax.set_title(titulo)
    plt.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=120)
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")

def generar_imagen_lineas(datos_grafica: dict, titulo: str) -> str:
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = datos_grafica.get("labels", [])
    
    for dataset in datos_grafica.get("datasets", []):
        color = dataset.get("borderColor") or dataset.get("backgroundColor")
        if isinstance(color, list):
            color = color[0]  # Evita el error si viene como array de colores
            
        ax.plot(
            labels,
            dataset.get("data", []),
            label=dataset.get("label"),
            color=color,
            marker='o',
            linewidth=1.5,
            markersize=4
        )
        
    ax.set_title(titulo, fontsize=9)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, fontsize=7, frameon=False)
    ax.tick_params(axis='both', which='major', labelsize=7)
    plt.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=120)
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")

@login_required
def descargar_pdf(request):
    resultado = IneAgregador.obtener_todo_unificado(tipo_analitica="panel_completo")
    datos_grafica = resultado.get("datos_grafica", {})
   

    contexto = {
        'informe_principal': resultado.get('datos', {}),
        'analisis_md': resultado.get('informe_ia', ''),
        'grafico_vegetal_b64': generar_imagen_barras(datos_grafica.get("vegetal", {}), "Evolución Producción Vegetal"),
        'grafico_animal_b64': generar_imagen_barras(datos_grafica.get("animal", {}), "Evolución Producción Animal"),
        'grafico_provincialtorta_b64': generar_imagen_torta(datos_grafica.get("provincial_anio", {}), "Distribución por Cultivos"),
        'grafico_provinciallinea_b64': generar_imagen_lineas(datos_grafica.get("provincial_anio", {}), "Distribución por Cultivos"),
    }

    template = get_template('ine/pdf_rendimientos.html')
    html = template.render(contexto, request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Informe_Rendimientos.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response