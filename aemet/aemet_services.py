from __future__ import annotations
import math
import logging
from datetime import date
import requests
from django.conf import settings
from django.core.cache import cache

from core.base_services import BaseDataService

logger = logging.getLogger(__name__)

# Clave y duración de la caché del inventario de estaciones.
# El listado de estaciones de AEMET apenas cambia (se dan de alta/baja muy de vez
# en cuando), así que no tiene sentido pedirlo a AEMET en cada clic del mapa:
# lo guardamos 24h y lo reutilizamos.
CACHE_KEY_INVENTARIO_ESTACIONES = "aemet_inventario_estaciones"
CACHE_TTL_INVENTARIO_SEGUNDOS = 60 * 60 * 24

# Cuántas estaciones cercanas se intentan como máximo antes de rendirse.
# No todas las estaciones del inventario de AEMET tienen datos climatológicos
# MENSUALES (algunas solo dan observación diaria/horaria), así que si la más
# cercana no tiene nada, se prueba con la siguiente más cercana, etc.
MAX_ESTACIONES_A_INTENTAR = 5


class Aemet(BaseDataService):
    URL_BASE_AEMET = "https://opendata.aemet.es/opendata/api"
    NUMERO_MESES_A_MOSTRAR = 6

    def __init__(self, identificador_estacion: str | None = None):
        self.identificador_estacion = identificador_estacion
        fecha_actual = date.today()
        self.anio_inicio = fecha_actual.year - 1
        self.anio_fin = fecha_actual.year
 
    # ------------------------------------------------------------------
    # Distancia entre dos puntos geográficos (fórmula de Haversine)
    # ------------------------------------------------------------------
    def _distancia_haversine_km(
        self, latitud_1: float, longitud_1: float, latitud_2: float, longitud_2: float
    ) -> float:
        """
        Calcula la distancia en línea recta (km) entre dos puntos de la Tierra
        dados por su latitud/longitud.

        No se puede restar las coordenadas como si fuera un plano: la Tierra es
        una esfera, así que un grado de longitud mide muchos km en el ecuador
        pero casi 0 km cerca de los polos. Esta fórmula (estándar, no hace falta
        modificarla) corrige esa curvatura:

        1. Convierte las diferencias de latitud/longitud a radianes.
        2. 'termino_a' combina esas diferencias en un solo valor intermedio.
        3. El resultado final es ese valor traducido a un ángulo y multiplicado
           por el radio de la Tierra (6371 km) -> distancia real en km.
        """
        radio_tierra_km = 6371.0
        diferencia_latitud = math.radians(latitud_2 - latitud_1)
        diferencia_longitud = math.radians(longitud_2 - longitud_1)
        termino_a = (
            math.sin(diferencia_latitud / 2) ** 2
            + math.cos(math.radians(latitud_1))
            * math.cos(math.radians(latitud_2))
            * math.sin(diferencia_longitud / 2) ** 2
        )
        return 2 * radio_tierra_km * math.atan2(math.sqrt(termino_a), math.sqrt(1 - termino_a))

    # ------------------------------------------------------------------
    # Inventario oficial de estaciones (reemplaza la lista fija ESTACIONES_AEMET)
    # ------------------------------------------------------------------
    @staticmethod
    def _coordenada_dms_a_decimal(valor: str | None) -> float | None:
        """
        El inventario de AEMET da las coordenadas en formato "GGMMSSH"
        (grados, minutos, segundos, hemisferio), por ejemplo:
            "424739N"   -> 42° 47' 39" Norte
            "0054041W"  -> 5° 40' 41" Oeste
        Esta función lo convierte a grados decimales (lo que usa el resto
        del código, p.ej. 42.588 en vez de "423137N").
        """
        if not valor:
            return None
        try:
            hemisferio = valor[-1].upper()
            cuerpo = valor[:-1]
            segundos = int(cuerpo[-2:])
            minutos = int(cuerpo[-4:-2])
            grados = int(cuerpo[:-4])
            decimal = grados + minutos / 60 + segundos / 3600
            if hemisferio in ("S", "W"):
                decimal = -decimal
            return decimal
        except (ValueError, IndexError):
            return None

    def _obtener_inventario_estaciones(self) -> list[dict]:
        """
        Pide a AEMET el listado COMPLETO y oficial de estaciones (código,
        nombre, latitud, longitud). Sustituye a la lista escrita a mano
        (que tenía al menos un código erróneo). Se cachea porque este
        listado no cambia de un día para otro.
        """
        estaciones_cacheadas = cache.get(CACHE_KEY_INVENTARIO_ESTACIONES)
        if estaciones_cacheadas is not None:
            return estaciones_cacheadas

        clave_api = getattr(settings, "AEMET_API_KEY", None)
        if not clave_api:
            raise RuntimeError("Falta la configuración settings.AEMET_API_KEY")

        url_metadatos = f"{self.URL_BASE_AEMET}/valores/climatologicos/inventarioestaciones/todasestaciones"

        respuesta_metadatos = requests.get(url_metadatos, headers={"api_key": clave_api}, timeout=10)
        respuesta_metadatos.raise_for_status()
        metadatos = respuesta_metadatos.json()

        url_descarga = metadatos.get("datos")
        if not url_descarga:
            logger.warning("AEMET no devolvió URL de datos para el inventario de estaciones: %s", metadatos)
            return []

        respuesta_datos = requests.get(url_descarga, timeout=15)
        respuesta_datos.raise_for_status()
        estaciones_crudas = respuesta_datos.json()

        estaciones = []
        for estacion_cruda in estaciones_crudas:
            latitud = self._coordenada_dms_a_decimal(estacion_cruda.get("latitud"))
            longitud = self._coordenada_dms_a_decimal(estacion_cruda.get("longitud"))
            identificador = estacion_cruda.get("indicativo")
            if latitud is None or longitud is None or not identificador:
                continue
            estaciones.append({
                "identificador": identificador,
                "nombre": estacion_cruda.get("nombre", ""),
                "latitud": latitud,
                "longitud": longitud,
            })

        cache.set(CACHE_KEY_INVENTARIO_ESTACIONES, estaciones, CACHE_TTL_INVENTARIO_SEGUNDOS)
        return estaciones

    def _estaciones_ordenadas_por_cercania(self, latitud: float, longitud: float) -> list[dict]:
        """Devuelve el inventario completo ordenado de más cercana a más lejana."""
        estaciones = self._obtener_inventario_estaciones()
        return sorted(
            estaciones,
            key=lambda estacion: self._distancia_haversine_km(
                latitud, longitud, estacion["latitud"], estacion["longitud"]
            ),
        )

    # ------------------------------------------------------------------
    # Descarga de datos climatológicos
    # ------------------------------------------------------------------
    def _fetch_estacion(self, identificador_estacion: str, clave_api: str) -> list[dict]:
        """Pide los datos climatológicos mensuales de UNA estación concreta."""
        url_metadatos = (
            f"{self.URL_BASE_AEMET}/valores/climatologicos/mensualesanuales/datos/"
            f"anioini/{self.anio_inicio}/aniofin/{self.anio_fin}/estacion/{identificador_estacion}"
        )

        respuesta_metadatos = requests.get(url_metadatos, headers={"api_key": clave_api}, timeout=10)
        respuesta_metadatos.raise_for_status()
        metadatos = respuesta_metadatos.json()

        url_descarga_datos = metadatos.get("datos")
        if not url_descarga_datos or metadatos.get("estado") == 404:
            logger.info(
                "AEMET sin datos climatológicos mensuales para la estación %s: %s",
                identificador_estacion,
                metadatos.get("descripcion", "sin descripción"),
            )
            return []

        respuesta_datos = requests.get(url_descarga_datos, timeout=15)
        respuesta_datos.raise_for_status()
        return respuesta_datos.json()

    def fetch(self, latitud: float = 0.0, longitud: float = 0.0) -> list[dict]:
        """
        Consulta la API de AEMET y devuelve los datos crudos en formato lista de
        diccionarios.
        """
        clave_api = getattr(settings, "AEMET_API_KEY", None)
        if not clave_api:
            raise RuntimeError("Falta la configuración settings.AEMET_API_KEY")

        if self.identificador_estacion:
            return self._fetch_estacion(self.identificador_estacion, clave_api)

        if not (latitud and longitud):
            raise ValueError(
                "Se necesita un identificador_estacion o una (latitud, longitud) "
                "para saber qué estación consultar."
            )

        candidatas = self._estaciones_ordenadas_por_cercania(latitud, longitud)
        if not candidatas:
            logger.warning("El inventario de estaciones de AEMET vino vacío.")
            return []

        for estacion in candidatas[:MAX_ESTACIONES_A_INTENTAR]:
            datos = self._fetch_estacion(estacion["identificador"], clave_api)
            if datos:
                self.identificador_estacion = estacion["identificador"]
                return datos

        logger.info(
            "Ninguna de las %s estaciones más cercanas a (%s, %s) tenía datos climatológicos mensuales.",
            len(candidatas[:MAX_ESTACIONES_A_INTENTAR]), latitud, longitud,
        )

        self.identificador_estacion = candidatas[0]["identificador"]
        return []

    def normalize(self, datos_brutos: list[dict]) -> dict:
        """
        Normaliza los datos de AEMET y los transforma en un JSON limpio
        listo para ser interpretado por Gemini o devuelto a una vista.
        """
        estacion_actual = self.identificador_estacion or "desconocida"

        if not datos_brutos:
            return {"estacion": estacion_actual, "registros": []}

        registros_limpios = []
        for fila in datos_brutos:
            fecha_str = str(fila.get("fecha", ""))
            if len(fecha_str) >= 7:
                try:
                    anio = int(fecha_str[:4])
                    mes = int(fecha_str[5:7])
                except ValueError:
                    continue
            else:
                continue

            
            if mes < 1 or mes > 12:
                continue

           
            p_val = str(fila.get("p_mes", 0)).strip().replace(",", ".")
            t_val = str(fila.get("tm_mes", 0)).strip().replace(",", ".")

           
            if p_val.lower() == "ip":
                precipitacion = 0.0
            else:
                try:
                    precipitacion = float(p_val) if p_val and p_val != "None" else float('nan')
                except ValueError:
                    precipitacion = float('nan')

            try:
                temperatura = float(t_val) if t_val and t_val != "None" else float('nan')
            except ValueError:
                temperatura = float('nan')

           
            if math.isnan(precipitacion) or math.isnan(temperatura):
                continue

            registros_limpios.append({
                "anio": anio,
                "mes": mes,
                "precipitacion_mensual_mm": precipitacion,
                "temperatura_media_mensual": temperatura,
            })

       
        registros_limpios = sorted(registros_limpios, key=lambda x: (x["anio"], x["mes"]))
        ultimos_registros = registros_limpios[-self.NUMERO_MESES_A_MOSTRAR:]

        return {
            "fuente": "AEMET OpenData",
            "estacion": estacion_actual,
            "total_registros": len(ultimos_registros),
            "registros": ultimos_registros
        }