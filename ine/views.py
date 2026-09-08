from django.shortcuts import render
from ine.agregador import IneAgregador


def vista_evolucion_agraria(request):
    resultado = IneAgregador.obtener_datos_para_grafica("panel_completo")
    print("RESULTADO INE AGREGADOR:", resultado)
    if resultado.get("estado") == "error":
        return render(request, "ine/rendimientos.html", {"mensaje_error": resultado.get("mensaje")})

    datos = resultado.get("datos_grafica", {})

    return render(
        request,
        "ine/rendimientos.html",
        {
            "datos_evolucion": datos,       # Contiene 'vegetal' y 'animal'
            "datos_provinciales": datos,    # Contiene 'evolucion_global' y 'provincial_anio'
        },
    )