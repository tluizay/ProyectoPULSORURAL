from __future__ import annotations
import logging
import requests
from core.base_services import BaseDataService

logger = logging.getLogger(__name__)


class Suelos(BaseDataService):
    URL_BASE_ITACYL = "https://servicios.itacyl.es/arcgis/rest/services/Visor_Suelos/MapServer"

    def fetch(self, lat: float, lng: float) -> list[dict] | None:
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

        respuesta_servidor = requests.get(
            f"{self.URL_BASE_ITACYL}/identify", 
            params=parametros_consulta, 
            timeout=5
        )
        respuesta_servidor.raise_for_status()
        
        datos_json = respuesta_servidor.json()
        return datos_json.get("results", [])

    def normalize(self, raw_data: list[dict] | None) -> dict:
        if not raw_data:
            return {
                "codigo_provincia": None,
                "nombre_municipio": None,
                "atributos_suelo": {}
            }

        atributos_acumulados = {}
        for resultado_capa in raw_data:
            atributos_capa = resultado_capa.get("attributes", {})
            atributos_acumulados.update(atributos_capa)

        return {
            "codigo_provincia": atributos_acumulados.get("C_PROVINCIA"),
            "nombre_municipio": atributos_acumulados.get("D_NOMBRE"),
            "atributos_suelo": atributos_acumulados
        }