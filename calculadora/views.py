from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


def asistente_calculadora(request):
    return render(request, "sigpac/mapa.html")


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required
def calcular(request):
    """
    Calculadora de productividad y métricas agrarias plurianual.
    Permite calcular proyecciones considerando un incremento anual (interés/inflación)
    en precios y costes a lo largo de varios años.

    Parámetros esperados (GET):
      - superficie_ha       (ha)
      - rendimiento_kg_ha   (kg/ha base)
      - precio_kg           (€/kg base)
      - coste_ha            (€/ha base)
      - anios               (ej: "2026,2027,2028" o un rango)
      - tasa_interes        (% de incremento anual estimado, ej: 2.5 para un 2.5%)
    """
    try:
        superficie_ha = float(request.GET.get("superficie_ha", ""))
        rendimiento_kg_ha = float(request.GET.get("rendimiento_kg_ha", ""))
        precio_kg = float(request.GET.get("precio_kg", ""))
        coste_ha = float(request.GET.get("coste_ha", 0) or 0)
        
        # Tasa de interés / incremento anual (porcentaje, ej: 2.0 -> 2%)
        tasa_interes = float(request.GET.get("tasa_interes", 0) or 0) / 100.0

        # Procesar los años (ejemplo: ?anios=2026,2027,2028)
        anios_raw = request.GET.get("anios", "")
        if anios_raw:
            lista_anios = [int(a.strip()) for a in anios_raw.split(",")]
        else:
            lista_anios = [] # Si no ponen años, se calcula solo una vez de forma estática

    except (TypeError, ValueError):
        return JsonResponse(
            {"error": "Revisa que los valores numéricos (superficie, rendimiento, precios, años o tasa) sean válidos."},
            status=400,
        )

    if superficie_ha <= 0 or rendimiento_kg_ha < 0 or precio_kg < 0:
        return JsonResponse(
            {"error": "La superficie debe ser mayor que 0 y los demás valores no pueden ser negativos."},
            status=400,
        )

    # Si el usuario no especificó años, devolvemos el cálculo base de un solo periodo
    if not lista_anios:
        produccion_total_kg = superficie_ha * rendimiento_kg_ha
        ingreso_total = produccion_total_kg * precio_kg
        coste_total = superficie_ha * coste_ha
        margen_total = ingreso_total - coste_total
        margen_por_ha = margen_total / superficie_ha

        return JsonResponse({
            "superficie_ha": round(superficie_ha, 4),
            "rendimiento_kg_ha": round(rendimiento_kg_ha, 2),
            "precio_kg": round(precio_kg, 4),
            "coste_ha": round(coste_ha, 2),
            "produccion_total_kg": round(produccion_total_kg, 2),
            "ingreso_total": round(ingreso_total, 2),
            "coste_total": round(coste_total, 2),
            "margen_total": round(margen_total, 2),
            "margen_por_ha": round(margen_por_ha, 2),
        })

    # Si hay varios años, proyectamos aplicando la tasa de interés/crecimiento compuesto
    proyeccion_anios = []
    
    # Tomamos el año base como el primer elemento de la lista para calcular el interés acumulado año con año
    anio_base = lista_anios[0]

    for i, anio in enumerate(lista_anios):
        # Aplicamos la tasa de interés compuesta en función de los años transcurridos desde el inicio
        factor_crecimiento = (1 + tasa_interes) ** i

        precio_ajustado = precio_kg * factor_crecimiento
        coste_ajustado = coste_ha * factor_crecimiento  # Asumimos que los costes también suben con la inflación/interés

        produccion_total_kg = superficie_ha * rendimiento_kg_ha
        ingreso_total = produccion_total_kg * precio_ajustado
        coste_total = superficie_ha * coste_ajustado
        margen_total = ingreso_total - coste_total
        margen_por_ha = margen_total / superficie_ha if superficie_ha > 0 else 0

        proyeccion_anios.append({
            "anio": anio,
            "precio_kg": round(precio_ajustado, 4),
            "coste_ha": round(coste_ajustado, 2),
            "produccion_total_kg": round(produccion_total_kg, 2),
            "ingreso_total": round(ingreso_total, 2),
            "coste_total": round(coste_total, 2),
            "margen_total": round(margen_total, 2),
            "margen_por_ha": round(margen_por_ha, 2),
        })

    return JsonResponse(
        {
            "superficie_ha": round(superficie_ha, 4),
            "rendimiento_kg_ha": round(rendimiento_kg_ha, 2),
            "tasa_interes_anual_porcentaje": round(tasa_interes * 100, 2),
            "proyeccion": proyeccion_anios,
        }
    )
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required
def calcular_grafica_comparativa(request):
    """
    Vista que devuelve los datos listos para una gráfica de líneas plurianual,
    incluyendo la estimación base y las bandas de sensibilidad del +2% y -2%.

    Parámetros esperados (GET):
      - superficie_ha       (ha)
      - rendimiento_kg_ha   (kg/ha base)
      - precio_kg           (€/kg base)
      - coste_ha            (€/ha base)
      - anios               (ej: "2026,2027,2028,2029")
      - tasa_interes        (% de incremento anual estimado, ej: 2.0)
    """
    try:
        superficie_ha = float(request.GET.get("superficie_ha", ""))
        rendimiento_base = float(request.GET.get("rendimiento_kg_ha", ""))
        precio_kg = float(request.GET.get("precio_kg", ""))
        coste_ha = float(request.GET.get("coste_ha", 0) or 0)
        tasa_interes = float(request.GET.get("tasa_interes", 0) or 0) / 100.0

        anios_raw = request.GET.get("anios", "")
        if anios_raw:
            lista_anios = [int(a.strip()) for a in anios_raw.split(",")]
        else:
            lista_anios = [2026, 2027, 2028, 2029, 2030]  # Por defecto si no pasan años
            
    except (TypeError, ValueError):
        return JsonResponse(
            {"error": "Parámetros numéricos inválidos."},
            status=400,
        )

    if superficie_ha <= 0 or rendimiento_base < 0 or precio_kg < 0:
        return JsonResponse(
            {"error": "La superficie debe ser mayor que 0 y los valores no pueden ser negativos."},
            status=400,
        )

    labels_anios = []
    datos_base = []
    datos_superior = []  # +2%
    datos_inferior = []  # -2%

    for i, anio in enumerate(lista_anios):
        labels_anios.append(str(anio))
        
        # Factor de crecimiento compuesto por los años transcurridos
        factor_crecimiento = (1 + tasa_interes) ** i
        precio_ajustado = precio_kg * factor_crecimiento

        # Rendimiento base y variantes de ±2% aplicadas al rendimiento o ingreso total
        prod_base = superficie_ha * rendimiento_base * precio_ajustado
        
        # Aplicamos la comparativa del 2% por encima y por debajo
        prod_superior = prod_base * 1.02
        prod_inferior = prod_base * 0.98

        datos_base.append(round(prod_base, 2))
        datos_superior.append(round(prod_superior, 2))
        datos_inferior.append(round(prod_inferior, 2))

    # Estructura JSON optimizada para librerías de gráficos como Chart.js
    return JsonResponse({
        "chart": {
            "labels": labels_anios,
            "datasets": [
                {
                    "label": "Estimación Base (Ingreso Total €)",
                    "data": datos_base,
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "fill": False
                },
                {
                    "label": "Escenario Optimista (+2%)",
                    "data": datos_superior,
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "borderDash": [5, 5],
                    "fill": False
                },
                {
                    "label": "Escenario Pesimista (-2%)",
                    "data": datos_inferior,
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderDash": [5, 5],
                    "fill": False
                }
            ]
        }
    })