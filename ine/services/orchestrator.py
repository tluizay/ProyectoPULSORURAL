from __future__ import annotations
from pathlib import Path
from .extractor import extraer_texto_archivo, EXTENSIONES_IMAGENES_PERMITIDAS
from .paser import parsear_tabla_resultados, extraer_anio_informe

def procesar_archivo_ceas(ruta_archivo: str | Path) -> dict:
    """Procesa un único archivo PDF o imagen y devuelve la estructura de datos limpia."""
    ruta_archivo = Path(ruta_archivo)
    texto_plano = extraer_texto_archivo(ruta_archivo)
    tabla_estructurada = parsear_tabla_resultados(texto_plano)

    return {
        "archivo_origen": ruta_archivo.name,
        "anio": extraer_anio_informe(texto_plano, ruta_archivo.name),
        "moneda": "EUR",
        "unidad": "millones",
        "tabla_resultados_renta_agraria": tabla_estructurada,
    }

def procesar_directorio_ceas(ruta_directorio: str | Path) -> list[dict]:
    """Procesa de forma masiva todos los archivos válidos contenidos en un directorio."""
    ruta_directorio = Path(ruta_directorio)
    extensiones_validas = {".pdf", *EXTENSIONES_IMAGENES_PERMITIDAS}
    
    archivos_encontrados = sorted(
        archivo for archivo in ruta_directorio.iterdir() 
        if archivo.suffix.lower() in extensiones_validas
    )
    
    return [procesar_archivo_ceas(archivo) for archivo in archivos_encontrados]