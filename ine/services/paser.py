from __future__ import annotations
import re
from typing import Optional

EXPRESION_REGULAR_NUMERO = r"-?\d{1,3}(?:\.\d{3})*,\d{1,2}"
EXPRESION_REGULAR_PORCENTAJE = r"\d{1,3}(?:,\d+)?%"

# Detecta líneas de tabla con formato: "Etiqueta ......... 1.234,56   45,6%"
PATRON_LINEA_TABLA = re.compile(rf"^(.+?)\s{{2,}}({EXPRESION_REGULAR_NUMERO})(?:\s+(.+))?\s*$")
PATRON_NIVEL_SUPERIOR = re.compile(r"^([A-H])\.\s*(.+)$")
PATRON_FILA_NUMERADA = re.compile(r"^\d+\.\s*(.+)$")

ANCLA_INICIO_TABLA = re.compile(r"A\.\s*Producci[oó]n rama agraria")
ANCLA_FIN_TABLA = re.compile(r"H\.\s*Renta agraria")

SUBSECCIONES_BAJO_A = {"producción vegetal", "producción animal", "producción de servicios"}

def _convertir_texto_a_flotante(cadena_numero: str) -> float:
    """Convierte un string numérico con formato español (ej: 1.234,56) a float."""
    return float(cadena_numero.replace(".", "").replace(",", "."))

def _extraer_porcentaje(texto_opcional: Optional[str]) -> Optional[float]:
    """Extrae el valor porcentual de la columna de la derecha, si existe."""
    if not texto_opcional:
        return None
    coincidencia = re.search(EXPRESION_REGULAR_PORCENTAJE, texto_opcional)
    if not coincidencia:
        return None
    return float(coincidencia.group(0).rstrip("%").replace(",", "."))

def _normalizar_etiqueta(etiqueta: str) -> str:
    """Limpia espacios múltiples, pasa a minúsculas y elimina puntos finales."""
    return re.sub(r"\s+", " ", etiqueta).strip().lower().rstrip(".")

def parsear_tabla_resultados(texto_documento: str) -> dict:
    """Analiza el texto plano y extrae la tabla de resultados de Renta Agraria en un JSON anidado."""
    lineas_texto = texto_documento.splitlines()
    indice_inicio = None
    indice_fin = None
    
    for indice, linea in enumerate(lineas_texto):
        if indice_inicio is None and ANCLA_INICIO_TABLA.search(linea):
            indice_inicio = indice
        if indice_inicio is not None and ANCLA_FIN_TABLA.search(linea):
            indice_fin = indice
            break

    if indice_inicio is None or indice_fin is None:
        return {"encontrada": False, "items": []}

    lista_secciones_principales: list[dict] = []
    seccion_superior_actual: Optional[dict] = None
    subseccion_produccion_actual: Optional[dict] = None
    subseccion_ganadera_actual: Optional[dict] = None

    for linea_cruda in lineas_texto[indice_inicio : indice_fin + 1]:
        if not linea_cruda.strip():
            continue

        coincidencia_linea = PATRON_LINEA_TABLA.match(linea_cruda)
        if not coincidencia_linea:
            continue

        etiqueta_cruda, valor_crudo, resto_linea = coincidencia_linea.groups()
        etiqueta_limpia = re.sub(r"\s+", " ", etiqueta_cruda).strip()
        valor_numerico = _convertir_texto_a_flotante(valor_crudo)
        porcentaje_calculado = _extraer_porcentaje(resto_linea)

        # 1. Detectar categorías principales de la A a la H
        coincidencia_nivel_superior = PATRON_NIVEL_SUPERIOR.match(etiqueta_limpia)
        if coincidencia_nivel_superior:
            codigo_categoria, nombre_categoria = coincidencia_nivel_superior.groups()
            seccion_superior_actual = {
                "codigo": codigo_categoria,
                "etiqueta": nombre_categoria.strip(),
                "valor_millones_eur": valor_numerico,
                "porcentaje": porcentaje_calculado,
                "detalle": [],
            }
            lista_secciones_principales.append(seccion_superior_actual)
            subseccion_produccion_actual = None
            subseccion_ganadera_actual = None
            continue

        etiqueta_normalizada = _normalizar_etiqueta(etiqueta_limpia)

        # 2. Detectar subsecciones dentro de la Producción Rama Agraria (A)
        if etiqueta_normalizada in SUBSECCIONES_BAJO_A:
            nodo_subseccion = {
                "etiqueta": etiqueta_limpia,
                "valor_millones_eur": valor_numerico,
                "porcentaje": porcentaje_calculado,
                "detalle": []
            }
            if seccion_superior_actual is not None:
                seccion_superior_actual["detalle"].append(nodo_subseccion)
            subseccion_ganadera_actual = None
            subseccion_produccion_actual = nodo_subseccion if etiqueta_normalizada != "producción de servicios" else None
            continue

        if etiqueta_normalizada.startswith("otras producciones"):
            nodo_otras = {
                "etiqueta": etiqueta_limpia,
                "valor_millones_eur": valor_numerico,
                "porcentaje": porcentaje_calculado,
                "detalle": []
            }
            if seccion_superior_actual is not None:
                seccion_superior_actual["detalle"].append(nodo_otras)
            subseccion_produccion_actual = None
            subseccion_ganadera_actual = None
            continue

        if etiqueta_normalizada in {"carne y ganado", "productos animales"}:
            nodo_ganadero = {
                "etiqueta": etiqueta_limpia,
                "valor_millones_eur": valor_numerico,
                "porcentaje": porcentaje_calculado,
                "detalle": []
            }
            if subseccion_produccion_actual is not None:
                subseccion_produccion_actual["detalle"].append(nodo_ganadero)
            subseccion_ganadera_actual = nodo_ganadero
            continue

        # 3. Detectar elementos numerados internos
        coincidencia_numerada = PATRON_FILA_NUMERADA.match(etiqueta_limpia)
        if coincidencia_numerada:
            nodo_item = {
                "etiqueta": etiqueta_limpia,
                "valor_millones_eur": valor_numerico,
                "porcentaje": porcentaje_calculado
            }
            if subseccion_ganadera_actual is not None:
                subseccion_ganadera_actual["detalle"].append(nodo_item)
            elif subseccion_produccion_actual is not None:
                subseccion_produccion_actual["detalle"].append(nodo_item)
            elif seccion_superior_actual is not None:
                seccion_superior_actual["detalle"].append(nodo_item)
            continue

        # Elementos genéricos restantes
        nodo_generico = {
            "etiqueta": etiqueta_limpia,
            "valor_millones_eur": valor_numerico,
            "porcentaje": porcentaje_calculado
        }
        if seccion_superior_actual is not None:
            seccion_superior_actual.setdefault("detalle", []).append(nodo_generico)

    return {"encontrada": True, "items": lista_secciones_principales}

def extraer_anio_informe(texto_documento: str, nombre_archivo: str) -> Optional[int]:
    """Extrae el año del informe buscando en el texto o en el nombre del fichero."""
    coincidencia_texto = re.search(r"(?:CEAS?|Año)\D{0,15}(20\d{2})", texto_documento)
    if coincidencia_texto:
        return int(coincidencia_texto.group(1))
        
    coincidencia_nombre = re.search(r"(20\d{2})", nombre_archivo)
    if coincidencia_nombre:
        return int(coincidencia_nombre.group(1))
        
    return None