from __future__ import annotations
import csv
import io
import unicodedata
import requests


def normalizar_texto(texto: str) -> str:
    """Quita acentos y pasa a minúsculas para comparar nombres fácilmente."""
    texto_sin_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    return texto_sin_acentos.strip().lower()


class Municipios:
    URL_DICIONARIO_INE = "https://www.ine.es/daco/daco42/codmun/diccionario25.csv"

    def __init__(self):
        self._codigo_a_nombre: dict[str, str] = {}
        self._nombre_a_codigo: dict[str, str] = {}
        self._codigo_a_provincia: dict[str, str] = {}  # "24" -> "León"
        self._datos_cargados: bool = False

    def _cargar_datos(self) -> None:
        """Descarga el CSV del INE y rellena los diccionarios de búsqueda."""
        if self._datos_cargados:
            return

        respuesta = requests.get(self.URL_DICIONARIO_INE, timeout=15)
        respuesta.raise_for_status()

        contenido_texto = respuesta.content.decode("latin-1")
        archivo_virtual = io.StringIO(contenido_texto)
        lector_csv = csv.DictReader(archivo_virtual, delimiter=";")

        for fila in lector_csv:
            datos_fila = {columna.strip(): valor.strip() for columna, valor in fila.items() if columna}

            codigo_provincia = datos_fila.get("CPRO", "").zfill(2)
            codigo_municipio = datos_fila.get("CMUN", "").zfill(3)
            nombre_municipio = datos_fila.get("NOMBRE", "")
            nombre_provincia = datos_fila.get("PROVINCIA", "")  # Columna de provincia del INE

            if codigo_provincia and codigo_municipio and nombre_municipio:
                codigo_ine_completo = f"{codigo_provincia}{codigo_municipio}"
                nombre_normalizado = normalizar_texto(nombre_municipio)

                self._codigo_a_nombre[codigo_ine_completo] = nombre_municipio
                self._nombre_a_codigo[nombre_normalizado] = codigo_ine_completo

                if nombre_provincia:
                    self._codigo_a_provincia[codigo_provincia] = nombre_provincia

        self._datos_cargados = True

    def obtener_nombre_por_codigo(self, codigo_ine: str) -> str | None:
        """Devuelve el nombre del municipio dado su código INE (ejemplo: '24115')."""
        self._cargar_datos()
        codigo_limpio = str(codigo_ine).strip().zfill(5)
        return self._codigo_a_nombre.get(codigo_limpio)

    def obtener_codigo_por_nombre(self, nombre_municipio: str) -> str | None:
        """Devuelve el código INE dado el nombre del municipio (ejemplo: 'Leon')."""
        self._cargar_datos()
        nombre_limpio = normalizar_texto(nombre_municipio)
        return self._nombre_a_codigo.get(nombre_limpio)

    def obtener_provincia_por_codigo(self, codigo_provincia: str | int) -> str | None:
        """Devuelve el nombre de la provincia dado su código de 2 dígitos (ejemplo: '24' o 24 -> 'León')."""
        self._cargar_datos()
        codigo_limpio = str(codigo_provincia).strip().zfill(2)
        return self._codigo_a_provincia.get(codigo_limpio)