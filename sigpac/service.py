from __future__ import annotations

import logging
import requests
from core.base_services import BaseDataService


logger = logging.getLogger(__name__)


class SigpacPuntoService(BaseDataService):
    URL_COLECCION_ITEMS = "https://sigpac-hubcloud.es/ogcapi/collections/recintos/items"

    def fetch(self, latitud: float, longitud: float) -> dict | None:
        delta = 0.00005
        limite_geografico = f"{longitud - delta},{latitud - delta},{longitud + delta},{latitud + delta}"

        parametros_peticion = {
            "f": "json",
            "bbox": limite_geografico,
            "limit": 1
        }

        try:
            respuesta_servidor = requests.get(
                self.URL_COLECCION_ITEMS,
                params=parametros_peticion,
                timeout=10
            )

            if respuesta_servidor.status_code == 200:
                datos_json = respuesta_servidor.json()
                elementos_encontrados = datos_json.get("features", [])
                if elementos_encontrados:
                    return elementos_encontrados[0]
            else:
                logger.warning(f"SIGPAC OGC API respondió con código {respuesta_servidor.status_code}")

        except Exception as e:
            logger.error(f"Error de conexión al consultar SIGPAC: {e}")

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
                "agregado": None,
                "zona": None,
                "poligono": None,
                "parcela": None,
                "recinto": None,
                "pendiente_media": None,
                "altitud": None,
                "elegibilidad": None,       # no existe en el API actual
                "cap_resultante": None,     # no existe en el API actual
                "dn_perimeter": None,       # no existe en el API actual
                "geocentro_x": None,        # no existe en el API actual
                "geocentro_y": None,        # no existe en el API actual
                "geometria": None,
                "atributos_brutos": None,
            }

        propiedades = datos_brutos.get("properties") or datos_brutos.get("propiedades") or {}
        geometria_extraida = datos_brutos.get("geometry") or datos_brutos.get("geometria")

        provincias_ine = {
            24: "León", "24": "León",
            47: "Valladolid", "47": "Valladolid",
            34: "Palencia", "34": "Palencia",
            9: "Burgos", "09": "Burgos", "9": "Burgos",
            49: "Zamora", "49": "Zamora",
            37: "Salamanca", "37": "Salamanca",
            40: "Segovia", "40": "Segovia",
            42: "Soria", "42": "Soria",
            5: "Ávila", "05": "Ávila", "5": "Ávila"
        }

        cod_provincia = propiedades.get("provincia")

        # Resolución segura de provincia
        prov_key = int(cod_provincia) if str(cod_provincia).isdigit() else cod_provincia
        nombre_provincia = provincias_ine.get(
            prov_key,
            f"Provincia {cod_provincia}" if cod_provincia is not None else "No especificada"
        )

        return {
            "sin_recinto": False,
            "error": None,
            "provincia": nombre_provincia,
            "agregado": propiedades.get("agregado", 0),
            "zona": propiedades.get("zona", 0),
            "poligono": propiedades.get("poligono"),
            "parcela": propiedades.get("parcela"),
            "recinto": propiedades.get("recinto"),
            "pendiente_media": self._obtener_primer_valor(propiedades, "pendiente_media", valor_defecto=None),
            "altitud": self._obtener_primer_valor(propiedades, "altitud", valor_defecto=None),
            "elegibilidad": None,       # campo no disponible en el API actual
            "cap_resultante": None,     # campo no disponible en el API actual
            "dn_perimeter": None,       # campo no disponible en el API actual
            "geocentro_x": None,        # campo no disponible en el API actual
            "geocentro_y": None,        # campo no disponible en el API actual
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