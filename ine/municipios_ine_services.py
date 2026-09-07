from __future__ import annotations
import unicodedata
import requests
from io import BytesIO
import openpyxl


def normalizar_texto(texto: str) -> str:
    texto_sin_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    return texto_sin_acentos.strip().lower()


# Mapeo estático de provincia (no viene en el XLSX del INE)
_PROVINCIAS: dict[str, str] = {
"05": "Ávila", "24": "León", "37": "Salamanca",
"42": "Soria","47": "Valladolid", "49": "Zamora",
}


class Municipios:
    URL_DICIONARIO_INE = "https://www.ine.es/daco/daco42/codmun/26codmun.xlsx"

    def __init__(self):
        self._codigo_a_nombre: dict[str, str] = {}
        self._nombre_a_codigo: dict[str, str] = {}
        self._datos_cargados: bool = False

    def _cargar_datos(self) -> None:
        if self._datos_cargados:
            return

        respuesta = requests.get(self.URL_DICIONARIO_INE, timeout=15)
        respuesta.raise_for_status()

        libro = openpyxl.load_workbook(BytesIO(respuesta.content), read_only=True)
        hoja = libro.active

        # La primera fila es la cabecera: CPRO | CMUN | DC | NOMBRE
        for fila in hoja.iter_rows(min_row=2, values_only=True):
            if not fila or len(fila) < 4:
                continue

            codigo_provincia = str(fila[0]).strip().zfill(2)
            codigo_municipio = str(fila[1]).strip().zfill(3)
            nombre_municipio = str(fila[3]).strip() if fila[3] else ""

            if codigo_provincia and codigo_municipio and nombre_municipio:
                codigo_ine_completo = f"{codigo_provincia}{codigo_municipio}"
                nombre_normalizado = normalizar_texto(nombre_municipio)

                self._codigo_a_nombre[codigo_ine_completo] = nombre_municipio
                self._nombre_a_codigo[nombre_normalizado] = codigo_ine_completo

        libro.close()
        self._datos_cargados = True

    def obtener_nombre_por_codigo(self, codigo_ine: str) -> str | None:
        self._cargar_datos()
        codigo_limpio = str(codigo_ine).strip().zfill(5)
        return self._codigo_a_nombre.get(codigo_limpio)

    def obtener_codigo_por_nombre(self, nombre_municipio: str) -> str | None:
        self._cargar_datos()
        nombre_limpio = normalizar_texto(nombre_municipio)
        return self._nombre_a_codigo.get(nombre_limpio)

    def obtener_provincia_por_codigo(self, codigo_provincia: str | int) -> str | None:
        self._cargar_datos()
        codigo_limpio = str(codigo_provincia).strip().zfill(2)
        return _PROVINCIAS.get(codigo_limpio)   