from __future__ import annotations

import csv
import io
import logging
import re
import requests
from core.base_services import BaseDataService
from ine.municipios_ine_services import Municipios, normalizar_texto

logger = logging.getLogger(__name__)


class UsoSuelosIne(BaseDataService):
    URL_PLANTILLA_INE = "https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/{identificador_tabla}.csv"
    TABLA_MUNICIPIOS = "69305"

    def __init__(self, identificador_tabla: str = TABLA_MUNICIPIOS):
        self.identificador_tabla = identificador_tabla
        self.servicio_municipios = Municipios()

    def fetch(self, municipio_o_codigo: str) -> list[dict] | None:
        """Descarga la tabla del INE y filtra las filas correspondientes al municipio buscado."""
        url = self.URL_PLANTILLA_INE.format(identificador_tabla=self.identificador_tabla)
        encabezados = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}

        try:
            respuesta = requests.get(url, headers=encabezados, timeout=30)
            respuesta.raise_for_status()
        except requests.RequestException as e:
            logger.error("Error al descargar la tabla %s del INE: %s", self.identificador_tabla, e)
            return None

        contenido_texto = respuesta.content.decode("utf-8-sig")
        if not contenido_texto.strip():
            return []

        archivo_virtual = io.StringIO(contenido_texto)
        lector_csv = csv.reader(archivo_virtual, delimiter=";")

        try:
            cabeceras = next(lector_csv)
        except StopIteration:
            return []

        cabeceras_limpias = [str(col).strip().lower() for col in cabeceras]

        # 1. Determinar si el término introducido es nombre o código INE
        termino_limpio = municipio_o_codigo.strip()
        if termino_limpio.isdigit():
            codigo_buscado = termino_limpio.zfill(5)
            nombre_oficial = self.servicio_municipios.obtener_nombre_por_codigo(codigo_buscado)
        else:
            codigo_buscado = self.servicio_municipios.obtener_codigo_por_nombre(termino_limpio)
            nombre_oficial = self.servicio_municipios.obtener_nombre_por_codigo(codigo_buscado) if codigo_buscado else termino_limpio

        # 2. Filtrar las filas del CSV matching el nombre o código
        nombre_normalizado_buscado = normalizar_texto(nombre_oficial or termino_limpio)
        filas_filtradas = []

        for fila in lector_csv:
            if not fila:
                continue

            registro = {
                cabecera: valor.strip()
                for cabecera, valor in zip(cabeceras_limpias, fila)
            }

            # Buscar coincidencias en campos de texto de la fila (municipios)
            texto_fila = " ".join(registro.values())
            texto_fila_normalizado = normalizar_texto(texto_fila)

            if (codigo_buscado and codigo_buscado in texto_fila) or (nombre_normalizado_buscado in texto_fila_normalizado):
                filas_filtradas.append(registro)

        return filas_filtradas

    def normalize(self, raw_data: list[dict] | None) -> dict:
        if not raw_data:
            return {
                "registros_encontrados": 0,
                "registros": [],
            }

        primer_registro = raw_data[0]
        claves = list(primer_registro.keys())

        columna_indicador = claves[0]
        columna_periodo = "periodo" if "periodo" in claves else claves[2] if len(claves) > 2 else claves[0]
        columna_valor = "total" if "total" in claves else claves[-1]

        datos_por_anio: dict[int, dict] = {}

        for fila in raw_data:
            indicador_raw = fila.get(columna_indicador, "").strip()
            periodo_raw = fila.get(columna_periodo, "")
            valor_raw = fila.get(columna_valor, "")

            coincidencia_anio = re.search(r"\d{4}", str(periodo_raw))
            if not coincidencia_anio:
                continue
            anio = int(coincidencia_anio.group(0))

            valor_str = str(valor_raw).replace(".", "").replace(",", ".")
            try:
                valor = float(valor_str)
            except ValueError:
                continue

            if anio not in datos_por_anio:
                datos_por_anio[anio] = {"anio": anio}

            if indicador_raw and indicador_raw not in datos_por_anio[anio]:
                datos_por_anio[anio][indicador_raw] = valor

        anios_ordenados = sorted(datos_por_anio.keys())
        registros_ordenados = [datos_por_anio[anio] for anio in anios_ordenados]

        return {
            "registros_encontrados": len(registros_ordenados),
            "registros": registros_ordenados,
        }