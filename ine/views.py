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
    fig, ax = plt.subplots(figsize=(6, 4.2))  # más ancho para dejar hueco a la leyenda

    dataset = datos_grafica.get("datasets", [{}])[0]
    data = dataset.get("data", [])
    labels = datos_grafica.get("labels", [])
    colors = dataset.get("backgroundColor")

    # Umbral: no mostrar % dentro de porciones demasiado pequeñas (se solapan)
    total = sum(data) if data else 1
    def autopct_filtrado(pct):
        return f"{pct:.1f}%" if pct >= 2.5 else ""

    wedges, _, autotexts = ax.pie(
        data,
        labels=None,              # quitamos las etiquetas pegadas al pastel
        colors=colors,
        autopct=autopct_filtrado,
        pctdistance=0.75,
        textprops={"fontsize": 7, "color": "white", "weight": "bold"},
        startangle=90,
    )

    ax.set_title(titulo)

    # Leyenda con nombre + porcentaje real, fuera del pastel
    porcentajes = [f"{l} ({(v/total)*100:.1f}%)" for l, v in zip(labels, data)]
    ax.legend(
        wedges,
        porcentajes,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        fontsize=7,
        frameon=False,
    )

    plt.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")

def generar_imagen_lineas(datos_grafica: dict, titulo: str) -> str:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    labels = datos_grafica.get("labels", [])

    for dataset in datos_grafica.get("datasets", []):
        color = dataset.get("borderColor") or dataset.get("backgroundColor")
        if isinstance(color, list):
            color = color[0]

        ax.plot(
            labels,
            dataset.get("data", []),
            label=dataset.get("label"),
            color=color,
            marker='o',
            linewidth=1.5,
            markersize=4
        )

    ax.set_title(titulo, fontsize=9, pad=25)  # más espacio bajo el título

    # Leyenda debajo del título pero fuera del área de las etiquetas del eje X
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=2, fontsize=7, frameon=False)

    # Rotar las etiquetas del eje X y alinearlas para que no se solapen
    ax.tick_params(axis='both', which='major', labelsize=7)
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right', rotation_mode='anchor')

    plt.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=120, bbox_inches="tight")
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
        'grafico_provincialtorta_b64': generar_imagen_torta(datos_grafica.get("provincial_anio", {}), "Distribución por Cultivos "),
        'grafico_provinciallinea_b64': generar_imagen_lineas(datos_grafica.get("provincial_anio", {}), "Distribución historico global"),
    } 

    template = get_template('ine/pdf_rendimientos.html')
    html = template.render(contexto, request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Informe_Rendimientos.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response