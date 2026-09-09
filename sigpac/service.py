from __future__ import annotations

import logging
import requests
from core.base_services import BaseDataService

logger = logging.getLogger(__name__)


class SigpacPuntoService(BaseDataService):
    URL_COLECCION_ITEMS = "https://sigpac-hubcloud.es/ogcapi/collections/recintos/items"

    def fetch(self, latitud: float, longitud: float) -> dict | None:
        delta_coordenadas = 0.00005
        limite_geografico = (
            f"{longitud - delta_coordenadas},"
            f"{latitud - delta_coordenadas},"
            f"{longitud + delta_coordenadas},"
            f"{latitud + delta_coordenadas}"
        )

        parametros_peticion = {
            "f": "json",
            "bbox": limite_geografico, #sigipac OGC API - Features de SIGPAC acepta parámetros de filtrado como bbox (Bounding Box o cuadro delimitador)
            "limit": 1
        }

        respuesta_servidor = requests.get(
            self.URL_COLECCION_ITEMS, 
            params=parametros_peticion, 
            timeout=10
        )

        if respuesta_servidor.status_code != 200:
            logger.warning(
                f"SIGPAC OGC API respondió con código de estado {respuesta_servidor.status_code}"
            )
            return None

        datos_json = respuesta_servidor.json()
        elementos_encontrados = datos_json.get("features", [])

        if elementos_encontrados:
            return elementos_encontrados[0]

        return None

    @staticmethod
    def _obtener_primer_valor(propiedades: dict, *nombres_posibles, valor_defecto=None):
        for nombre in nombres_posibles:
            if nombre in propiedades and propiedades[nombre] not in (None, ""):
                return propiedades[nombre]
        return valor_defecto

    def normalize(self, datos_brutos: dict | None) -> dict:
        if not datos_brutos:
            return {
                "sin_recinto": True,
                "error": None,
                "provincia": None,
                "municipio": None,
                "agregado": None,
                "zona": None,
                "poligono": None,
                "parcela": None,
                "recinto": None,
                "superficie_ha": None,
                "uso": None,
                "geometria": None,
                "atributos_brutos": None,
            }

       
        propiedades = datos_brutos.get("properties") or datos_brutos.get("propiedades") or {}
        geometria_extraida = datos_brutos.get("geometry") or datos_brutos.get("geometria")

        # Diccionarios de mapeo INE para traducir códigos a nombres de texto
        provincias_ine = {
            24: "León",
            47: "Valladolid",
            34: "Palencia",
            9: "Burgos",
            49: "Zamora",
            37: "Salamanca",
            40: "Segovia",
            42: "Soria",
            5: "Ávila"
        }

        municipios_ine = {
            "24-226": "Villaquilambre",
            "24-89": "León",
            "47-186": "Villaobispo de Regueras",
            "47-900": "Valladolid",
        }

        
        cod_provincia = propiedades.get("provincia")
        cod_municipio = propiedades.get("municipio")

        
        nombre_provincia = provincias_ine.get(cod_provincia, f"Provincia {cod_provincia}")
        clave_muni = f"{cod_provincia}-{cod_municipio}"
        nombre_municipio = municipios_ine.get(clave_muni, f"Municipio {cod_municipio}")

       
        uso_detectado = propiedades.get("uso") or propiedades.get("uso_sigpac") or "No especificado"
        superficie_val = propiedades.get("superficie_ha") or propiedades.get("superficie") or "N/D"

        return {
            "sin_recinto": False,
            "error": None,
            "provincia": nombre_provincia,
            "municipio": nombre_municipio,
            "agregado": propiedades.get("agregado", 0),
            "zona": propiedades.get("zona", 0),
            "poligono": propiedades.get("poligono"),
            "parcela": propiedades.get("parcela"),
            "recinto": propiedades.get("recinto"),
            "superficie_ha": superficie_val,
            "uso": uso_detectado,
            "geometria": geometria_extraida,
            "atributos_brutos": propiedades,
        }

class SigpacAreaService(BaseDataService):
    URL_COLECCION_ITEMS = "https://sigpac-hubcloud.es/ogcapi/collections/recintos/items"

    def __init__(self, cuadro_delimitador: list[float] | None = None, limite_resultados: int = 50):
        self.cuadro_delimitador = cuadro_delimitador
        self.limite_resultados = limite_resultados

    def fetch(self, latitud: float = 0.0, longitud: float = 0.0) -> list[dict]:
        if not self.cuadro_delimitador:
            delta_coordenadas = 0.01
            self.cuadro_delimitador = [
                longitud - delta_coordenadas,
                latitud - delta_coordenadas,
                longitud + delta_coordenadas,
                latitud + delta_coordenadas
            ]

        cadena_cuadro_delimitador = ",".join(map(str, self.cuadro_delimitador))

        parametros_peticion = {
            "f": "json",
            "bbox": cadena_cuadro_delimitador,
            "limit": self.limite_resultados
        }

        respuesta_servidor = requests.get(
            self.URL_COLECCION_ITEMS, 
            params=parametros_peticion, 
            timeout=15
        )
        respuesta_servidor.raise_for_status()

        datos_json = respuesta_servidor.json()
        return datos_json.get("features", [])

    def normalize(self, datos_brutos: list[dict]) -> dict:
        recintos_normalizados = []

        for elemento_recinto in datos_brutos:
            recintos_normalizados.append({
                "identificador_recinto": elemento_recinto.get("id"),
                "propiedades_recinto": elemento_recinto.get("properties", {}),
                "geometria": elemento_recinto.get("geometry", None)
            })

        return {
            "cantidad_recintos": len(recintos_normalizados),
            "recintos": recintos_normalizados
        }