from __future__ import annotations

def datos_produccion_vegetal(lista_informes: list[dict]) -> dict:
    """Prepara la serie temporal plurianual exclusivamente para la Producción Vegetal."""
    lista_ordenada = sorted(lista_informes, key=lambda x: x.get("anio") or 0)
    
    anios = []
    valores_vegetal = []

    for informe in lista_ordenada:
        anios.append(str(informe.get("anio")))
        
        # Buscamos dentro de la estructura anidada de la tabla
        items_tabla = informe.get("tabla_resultados_renta_agraria", {}).get("items", [])
        valor_encontrado = 0.0

        for item in items_tabla:
            # La categoría principal A contiene las subsecciones en su detalle
            if item.get("codigo") == "A":
                for subdetalle in item.get("detalle", []):
                    # Normalizamos la etiqueta para asegurarnos de encontrarla
                    etiqueta = subdetalle.get("etiqueta", "").lower()
                    if "producción vegetal" in etiqueta:
                        valor_encontrado = subdetalle.get("valor_millones_eur", 0.0)
                        break

        valores_vegetal.append(valor_encontrado)

    return {
        "labels": anios,
        "datasets": [
            {
                "label": "Producción Vegetal (Millones €)",
                "data": valores_vegetal,
                "backgroundColor": "rgba(40, 167, 69, 0.7)",  # Verde para vegetal
                "borderColor": "rgba(40, 167, 69, 1)",
                "borderWidth": 1
            }
        ]
    }


def datos_produccion_animal(lista_informes: list[dict]) -> dict:
    """Prepara la serie temporal plurianual exclusivamente para la Producción Animal."""
    lista_ordenada = sorted(lista_informes, key=lambda x: x.get("anio") or 0)
    
    anios = []
    valores_animal = []

    for informe in lista_ordenada:
        anios.append(str(informe.get("anio")))
        
        items_tabla = informe.get("tabla_resultados_renta_agraria", {}).get("items", [])
        valor_encontrado = 0.0

        for item in items_tabla:
            if item.get("codigo") == "A":
                for subdetalle in item.get("detalle", []):
                    etiqueta = subdetalle.get("etiqueta", "").lower()
                    if "producción animal" in etiqueta:
                        valor_encontrado = subdetalle.get("valor_millones_eur", 0.0)
                        break

        valores_animal.append(valor_encontrado)

    return {
        "labels": anios,
        "datasets": [
            {
                "label": "Producción Animal (Millones €)",
                "data": valores_animal,
                "backgroundColor": "rgba(23, 162, 184, 0.7)",  # Azul/Cyan para animal
                "borderColor": "rgba(23, 162, 184, 1)",
                "borderWidth": 1
            }
        ]
    }