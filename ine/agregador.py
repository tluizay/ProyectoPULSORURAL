import json
import logging
from ine.municipios_ine_services import Municipios
from ine.rendimiento_services import RendimientosIne
from ine.uso_suelos_services import UsoSuelosIne
from ine.gemini_services import asistente_virtual

logger = logging.getLogger(__name__)


class IneAgregador:

    @staticmethod
    def obtener_analisis_completo(codigo_municipio: str | None = None, latitud: float = 0.0, longitud: float = 0.0) -> dict:
        """
        Orquesta la consulta de datos del INE (municipios, rendimientos y usos del suelo),
        valida la presencia de registros y los envía a Gemini para generar un informe consolidado.
        """
        try:
            # 1. Extracción y normalización de cada servicio
            municipios_service = Municipios()
            datos_brutos_mun = municipios_service.fetch(codigo_municipio=codigo_municipio, latitud=latitud, longitud=longitud)
            json_municipios = municipios_service.normalize(datos_brutos_mun)

            rendimiento_service = RendimientosIne()
            datos_brutos_ren = rendimiento_service.fetch(codigo_municipio=codigo_municipio)
            json_rendimientos = rendimiento_service.normalize(datos_brutos_ren)

            suelos_service = UsoSuelosIne()
            datos_brutos_sue = suelos_service.fetch(codigo_municipio=codigo_municipio)
            json_usosuelos = suelos_service.normalize(datos_brutos_sue)

            # 2. Validaciones de datos mínimos
            if not json_municipios.get("registros"):
                return {
                    "estado": "error",
                    "mensaje": "No hemos encontrado el municipio especificado."
                }

            if not json_rendimientos.get("registros"):
                return {
                    "estado": "error",
                    "mensaje": "No hemos encontrado rendimientos para esta zona."
                }

            if not json_usosuelos.get("registros"):
                return {
                    "estado": "error",
                    "mensaje": "No hemos encontrado información de uso de suelos."
                }

            # 3. Empaquetado de contexto para la IA
            contexto_datos = {
                "municipio": json_municipios,
                "rendimientos": json_rendimientos,
                "uso_suelos": json_usosuelos
            }
            
            # Serialización correcta a JSON string
            contexto_json_str = json.dumps(contexto_datos, ensure_ascii=False, indent=2)

            # 4. Generación de informe con Gemini
            informe_ia = asistente_virtual(contexto_json_str)

            # 5. Respuesta consolidada para la Vista
            return {
                "estado": "exito",
                "datos": contexto_datos,
                "informe_ia": informe_ia
            }

        except Exception as e:
            logger.error(f"Error durante el proceso de agregación INE: {e}", exc_info=True)
            return {
                "estado": "error",
                "mensaje": "Ocurrió un error inesperado al procesar el informe de la zona."
            }