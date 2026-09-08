from __future__ import annotations

def evolucion_global(lista_informes: list[dict]) -> dict:
    """Prepara la serie para los datos globales de la comunidad a lo largo del histórico."""
    lista_ordenada = sorted(lista_informes, key=lambda x: x.get("anio") or 0)
    
    anios = []
    totales_vegetal = []
    cereales = []
    plantas_industriales = []
    plantas_forrajeras = []

    for informe in lista_ordenada:
        anio = informe.get("anio")
        if not anio:
            continue
            
        anios.append(str(anio))
        
        # 🔑 Usamos la clave correcta que nos dio la terminal
        tabla_datos = informe.get("tabla_resultados_renta_agraria", {})
        items = tabla_datos.get("items", [])
        
        val_veg = 0.0
        val_cereales = 0.0
        val_industriales = 0.0
        val_forrajeras = 0.0

        # Buscamos dentro de la sección A (Producción rama agraria)
        for seccion in items:
            if seccion.get("codigo") == "A":
                for sub in seccion.get("detalle", []):
                    etiqueta_sub = sub.get("etiqueta", "").lower()
                    
                    if "producción vegetal" in etiqueta_sub:
                        val_veg = sub.get("valor_millones_eur", 0.0)
                        for item_det in sub.get("detalle", []):
                            et_det = item_det.get("etiqueta", "").lower()
                            
                            if "cereales" in et_det:
                                val_cereales = item_det.get("valor_millones_eur", 0.0)
                            elif "industriales" in et_det:
                                val_industriales = item_det.get("valor_millones_eur", 0.0)
                            elif "forrajeras" in et_det:
                                val_forrajeras = item_det.get("valor_millones_eur", 0.0)

        totales_vegetal.append(val_veg)
        cereales.append(val_cereales)
        plantas_industriales.append(val_industriales)
        plantas_forrajeras.append(val_forrajeras)

    return {
        "labels": anios,
        "datasets": [
            {
                "label": "Producción Vegetal Total",
                "data": totales_vegetal,
                "borderColor": "#198754",
                "backgroundColor": "rgba(25, 135, 84, 0.1)",
                "borderWidth": 3,
                "tension": 0.2,
                "fill": True
            },
            {
                "label": "Cereales",
                "data": cereales,
                "borderColor": "#ffc107",
                "backgroundColor": "transparent",
                "borderWidth": 2,
                "tension": 0.2
            },
            {
                "label": "Plantas industriales",
                "data": plantas_industriales,
                "borderColor": "#0dcaf0",
                "backgroundColor": "transparent",
                "borderWidth": 2,
                "tension": 0.2
            },
            {
                "label": "Plantas forrajeras",
                "data": plantas_forrajeras,
                "borderColor": "#6c757d",
                "backgroundColor": "transparent",
                "borderWidth": 2,
                "tension": 0.2
            }
        ]
    }

def desglose_provincial_anio(lista_informes: list[dict], anio_objetivo: int | None = None) -> dict:
    """Prepara el desglose en gráfico de torta de los principales cultivos para el año seleccionado."""
    if not lista_informes:
        return {"labels": [], "datasets": []}

    if anio_objetivo is None:
        lista_ordenada = sorted(lista_informes, key=lambda x: x.get("anio") or 0, reverse=True)
        informe_seleccionado = lista_ordenada[0]
    else:
        informe_seleccionado = next((inf for inf in lista_informes if inf.get("anio") == anio_objetivo), lista_informes[0])

    cultivos_labels = []
    cultivos_valores = []

    tabla_datos = informe_seleccionado.get("tabla_resultados_renta_agraria", {})
    items = tabla_datos.get("items", [])

    # Buscamos dentro de la sección A -> Producción vegetal
    for seccion in items:
        if seccion.get("codigo") == "A":
            for sub in seccion.get("detalle", []):
                if "producción vegetal" in sub.get("etiqueta", "").lower():
                    for item_det in sub.get("detalle", []):
                        cultivos_labels.append(item_det.get("etiqueta", ""))
                        cultivos_valores.append(item_det.get("valor_millones_eur", 0.0))

    # Colores variados para las porciones de la torta
    colores = [
        '#198754', '#ffc107', '#0dcaf0', '#6c757d', 
        '#d63384', '#fd7e14', '#20c997', '#6f42c1', '#212529'
    ]

    return {
        "anio": informe_seleccionado.get("anio"),
        "labels": cultivos_labels if cultivos_labels else ["Sin datos"],
        "datasets": [
            {
                "label": f"Producción por Cultivos ({informe_seleccionado.get('anio')})",
                "data": cultivos_valores if cultivos_valores else [0.0],
                "backgroundColor": colores[:len(cultivos_labels)],
            }
        ]
    }