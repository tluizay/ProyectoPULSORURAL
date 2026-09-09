from __future__ import annotations

import logging
from pathlib import Path
import rasterio
import requests
import tenacity

from core.base_services import BaseDataService

logger = logging.getLogger(__name__)

# La carpeta de datos vive dentro de esta misma app: solgrids/data/solgrids/
DIRECTORIO_DATOS_SOILGRIDS = Path(__file__).resolve().parent / "data" / "soilgrids"

# Caché en memoria del CSV nacional de embalses (evita descargar y volver a
# parsear con pandas el ZIP completo del MITECO en cada petición). El Boletín
# Hidrológico se actualiza semanalmente (jueves), así que unas horas de caché
# son de sobra.
_CACHE_EMBALSES: dict[str, object] = {"dataframe": None, "timestamp": 0.0}
CACHE_TTL_EMBALSES_SEGUNDOS = 6 * 60 * 60  # 6 horas


@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
    retry=tenacity.retry_if_exception_type(requests.exceptions.RequestException),
    reraise=True,
)


class PropiedadesHidricas(BaseDataService):
    PROFUNDIDADES_EVALUADAS = ["0-5cm", "5-15cm", "15-30cm"]
    PROFUNDIDAD_UTIL_MAXIMA_CENTIMETROS = 100

    def _leer_pixel_raster(
        self, propiedad_suelo: str, profundidad: str, latitud: float, longitud: float
    ) -> float | None:
        ruta_archivo_raster = (
            DIRECTORIO_DATOS_SOILGRIDS / f"{propiedad_suelo}_mean_{profundidad}.tif"
        )
        if not ruta_archivo_raster.exists():
            logger.warning("No existe el raster esperado: %s", ruta_archivo_raster)
            return None

        with rasterio.open(str(ruta_archivo_raster)) as fuente_raster:
            # rasterio.index() espera (x, y), es decir (longitud, latitud) en
            # rasters geográficos EPSG:4326 — no (latitud, longitud), que es
            # la convención que usamos en el resto de la app.
            fila, columna = fuente_raster.index(longitud, latitud)
            if 0 <= fila < fuente_raster.height and 0 <= columna < fuente_raster.width:
                valor_pixel = fuente_raster.read(
                    1, window=((fila, fila + 1), (columna, columna + 1))
                )[0][0]
                if (
                    valor_pixel is not None
                    and valor_pixel != fuente_raster.nodata
                    and valor_pixel > -9999
                ):
                    return float(valor_pixel)
        return None

    def fetch(self, latitud: float, longitud: float) -> dict[str, list[float]]:
        valores_capacidad_campo = []
        valores_punto_marchitez = []

        for profundidad in self.PROFUNDIDADES_EVALUADAS:
            capacidad_campo_nivel = self._leer_pixel_raster(
                "wv0033", profundidad, latitud, longitud
            )
            punto_marchitez_nivel = self._leer_pixel_raster(
                "wv1500", profundidad, latitud, longitud
            )

            if capacidad_campo_nivel is not None:
                valores_capacidad_campo.append(capacidad_campo_nivel)
            if punto_marchitez_nivel is not None:
                valores_punto_marchitez.append(punto_marchitez_nivel)

        return {
            "valores_capacidad_campo": valores_capacidad_campo,
            "valores_punto_marchitez": valores_punto_marchitez,
        }

    def normalize(self, datos_brutos: dict[str, list[float]]) -> dict:
        valores_capacidad_campo = datos_brutos.get("valores_capacidad_campo", [])
        valores_punto_marchitez = datos_brutos.get("valores_punto_marchitez", [])

        if not valores_capacidad_campo or not valores_punto_marchitez:
            return {
                "datos_disponibles": False,
                "capacidad_campo": None,
                "punto_marchitez": None,
                "agua_util": None,
                "profundidad_util_centimetros": self.PROFUNDIDAD_UTIL_MAXIMA_CENTIMETROS,
            }

        promedio_capacidad_campo = (
            sum(valores_capacidad_campo) / len(valores_capacidad_campo)
        ) / 10
        promedio_punto_marchitez = (
            sum(valores_punto_marchitez) / len(valores_punto_marchitez)
        ) / 10
        agua_util_calculada = promedio_capacidad_campo - promedio_punto_marchitez

        return {
            "fuente_informacion": "SoilGrids Raster Local",
            "datos_disponibles": True,
            "capacidad_campo": round(promedio_capacidad_campo, 2),
            "punto_marchitez": round(promedio_punto_marchitez, 2),
            "agua_util": round(agua_util_calculada, 2),
            "profundidad_util_centimetros": self.PROFUNDIDAD_UTIL_MAXIMA_CENTIMETROS,
        }
