from __future__ import annotations
from .evolucion import datos_produccion_vegetal,datos_produccion_animal
from .provinciales import evolucion_global, desglose_provincial_anio

"se encarga de concentrar todas las graficas"

def disparador_analitica(tipo_grafica: str, lista_informes: list[dict], **kwargs) -> dict:
    if tipo_grafica == "panel_completo":
        return {
            "vegetal": datos_produccion_vegetal(lista_informes),
            "animal": datos_produccion_animal(lista_informes),
            "evolucion_global": evolucion_global(lista_informes),
            "provincial_anio": desglose_provincial_anio(lista_informes)
        }

    raise ValueError(f"Tipo de gráfica analítica no soportado: {tipo_grafica}")