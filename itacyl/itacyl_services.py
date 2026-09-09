from __future__ import annotations
import logging
import requests
from datetime import datetime
from core.base_services import BaseDataService

logger = logging.getLogger(__name__)


class Suelos(BaseDataService):
    URL_BASE_ITACYL = "https://servicios.itacyl.es/arcgis/rest/services/Visor_Suelos/MapServer"

    # 1. Hacemos que fetch acepte anio y mes (opcionales por si no se envían)
    def fetch(self, lat: float, lng: float, anio: int | None = None, mes: int | None = None) -> dict:
        """
        Consulta el servicio de suelos de ITACYL. 
        Aunque la API geográfica no suele cambiar por mes/año, los recibimos 
        para pasarlos al flujo de normalización y contexto.
        """
        parametros_consulta = {
            "geometry": f"{lng},{lat}",
            "geometryType": "esriGeometryPoint",
            "sr": "4326",
            "layers": "all",
            "tolerance": 5,
            "mapExtent": f"{lng - 0.01},{lat - 0.01},{lng + 0.01},{lat + 0.01}",
            "imageDisplay": "1000,1000,96",
            "returnGeometry": "false",
            "f": "json"
        }

        try:
            respuesta_servidor = requests.get(
                f"{self.URL_BASE_ITACYL}/identify", 
                params=parametros_consulta, 
                timeout=5
            )
            respuesta_servidor.raise_for_status()
            datos_json = respuesta_servidor.json()
            resultados = datos_json.get("results", [])
        except requests.RequestException as e:
            logger.error(f"Error al conectar con ITACYL: {e}")
            resultados = []

        # 2. Empaquetamos los datos crudos junto con el año y el mes 
        # para que el método normalize pueda leerlos.
        return {
            "raw_results": resultados,
            "anio": anio or datetime.now().year,
            "mes": mes or datetime.now().month
        }

    def normalize(self, raw_data: dict | None) -> dict:
        """
        Normaliza los datos de suelos e incorpora el año y el mes al diccionario de salida.
        """
        if not raw_data or not raw_data.get("raw_results"):
            return {
                "codigo_provincia": None,
                "nombre_municipio": None,
                "atributos_suelo": {},
                "anio": datetime.now().year,
                "mes": datetime.now().month
            }

        resultados_capa = raw_data["raw_results"]
        anio = raw_data.get("anio")
        mes = raw_data.get("mes")

        atributos_acumulados = {}
        for resultado_capa in resultados_capa:
            atributos_capa = resultado_capa.get("attributes", {})
            atributos_acumulados.update(atributos_capa)

        return {
            "codigo_provincia": atributos_acumulados.get("C_PROVINCIA"),
            "nombre_municipio": atributos_acumulados.get("D_NOMBRE"),
            "atributos_suelo": atributos_acumulados,
            "anio": anio,
            "mes": mes
        }