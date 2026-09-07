from django.shortcuts import render
from ine.agregador import IneAgregador


def api_ine(request):
    busqueda = request.GET.get("codigo_municipio") or request.GET.get("busqueda")

    # Si NO hay búsqueda (al abrir la página por primera vez), renderizamos la plantilla vacía
    if not busqueda or not busqueda.strip():
        return render(request, "ine/rendimientos.html", {})

    # Solo si el usuario envió un valor ejecutamos el agregador
    resultado = IneAgregador.obtener_analisis_completo(busqueda_municipio=busqueda)

    if resultado.get("estado") == "error":
        return render(
            request,
            "ine/rendimientos.html",
            {
                "mensaje_error": resultado.get("mensaje"),
                "codigo_municipio": busqueda,
            },
        )

    return render(
        request,
        "ine/rendimientos.html",
        {
            "datos_ine": resultado.get("datos"),
            "informe_ia": resultado.get("informe_ia"),
            "codigo_municipio": busqueda,
        },
    )