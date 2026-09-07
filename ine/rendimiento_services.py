from __future__ import annotations
import csv
import io
import re
import requests
from core.base_services import BaseDataService


class RendimientosIne(BaseDataService):
    URL_PLANTILLA_INE = "https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/{identificador_tabla}.csv"

    def __init__(self, identificador_tabla: str = "60233"):
        self.identificador_tabla = identificador_tabla

    def fetch(self, lat: float = 0.0, lng: float = 0.0) -> list[dict]:
        url_descarga = self.URL_PLANTILLA_INE.format(
            identificador_tabla=self.identificador_tabla
        )
        encabezados_peticion = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
        }

        respuesta_servidor = requests.get(
            url_descarga, headers=encabezados_peticion, timeout=15
        )
        respuesta_servidor.raise_for_status()

        texto_csv = respuesta_servidor.text.strip()
        if not texto_csv:
            return []

        fichero_buffer = io.StringIO(texto_csv)
        lector_csv = csv.reader(fichero_buffer, delimiter=";")

        try:
            cabeceras = next(lector_csv)
        except StopIteration:
            return []

        cabeceras_limpias = [col.strip().lower() for col in cabeceras]

        filas = []
        for fila in lector_csv:
            if not fila:
                continue
            registro = {
                cabecera: valor.strip()
                for cabecera, valor in zip(cabeceras_limpias, fila)
            }
            filas.append(registro)

        return filas

    def normalize(self, raw_data: list[dict] | None) -> dict:
        if not raw_data:
            return {
                "registros_encontrados": 0,
                "registros": [],
            }

        primer_registro = raw_data[0]
        claves = list(primer_registro.keys())

        columna_cultivo = claves[0]
        columna_periodo = "periodo" if "periodo" in claves else claves[2] if len(claves) > 2 else claves[0]
        columna_valor = "total" if "total" in claves else claves[-1]

        registros_procesados = []

        for fila in raw_data:
            cultivo_raw = fila.get(columna_cultivo, "")
            periodo_raw = fila.get(columna_periodo, "")
            valor_raw = fila.get(columna_valor, "")

            coincidencia_anio = re.search(r"\d{4}", str(periodo_raw))
            if not coincidencia_anio:
                continue
            anio = int(coincidencia_anio.group(0))

            valor_str = str(valor_raw).replace(".", "").replace(",", ".")
            try:
                rendimiento = float(valor_str)
            except ValueError:
                continue

            cultivo = cultivo_raw.strip()
            if not cultivo:
                continue

            registros_procesados.append(
                {
                    "cultivo": cultivo,
                    "anio": anio,
                    "rendimiento_medio_kilogramos_hectarea": rendimiento,
                }
            )

        return {
            "registros_encontrados": len(registros_procesados),
            "registros": registros_procesados,
        }