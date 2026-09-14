from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required



def asistente_calculadora(request):
    return render(request, "sigpac/mapa.html")


@login_required
def calcular(request):
    """
    Calculadora simple de productividad de tierras.
    El usuario introduce TODOS los valores manualmente (no se precargan
    datos de SIGPAC porque no siempre están disponibles).

    Parámetros esperados (GET):
      - superficie_ha       (ha)
      - rendimiento_kg_ha   (kg/ha)
      - precio_kg           (€/kg)
      - coste_ha            (€/ha)  -> opcional, por defecto 0

    Devuelve producción total, ingreso, coste y margen (total y por hectárea).
    """
    try:
        superficie_ha = float(request.GET.get("superficie_ha", ""))
        rendimiento_kg_ha = float(request.GET.get("rendimiento_kg_ha", ""))
        precio_kg = float(request.GET.get("precio_kg", ""))
        coste_ha = float(request.GET.get("coste_ha", 0) or 0)
    except (TypeError, ValueError):
        return JsonResponse(
            {"error": "Revisa que superficie, rendimiento y precio sean números válidos."},
            status=400,
        )

    if superficie_ha <= 0 or rendimiento_kg_ha < 0 or precio_kg < 0:
        return JsonResponse(
            {"error": "La superficie debe ser mayor que 0 y los demás valores no pueden ser negativos."},
            status=400,
        )

    produccion_total_kg = superficie_ha * rendimiento_kg_ha
    ingreso_total = produccion_total_kg * precio_kg
    coste_total = superficie_ha * coste_ha
    margen_total = ingreso_total - coste_total
    margen_por_ha = margen_total / superficie_ha

    return JsonResponse(
        {
            "superficie_ha": round(superficie_ha, 4),
            "rendimiento_kg_ha": round(rendimiento_kg_ha, 2),
            "precio_kg": round(precio_kg, 4),
            "coste_ha": round(coste_ha, 2),
            "produccion_total_kg": round(produccion_total_kg, 2),
            "ingreso_total": round(ingreso_total, 2),
            "coste_total": round(coste_total, 2),
            "margen_total": round(margen_total, 2),
            "margen_por_ha": round(margen_por_ha, 2),
        }
    )