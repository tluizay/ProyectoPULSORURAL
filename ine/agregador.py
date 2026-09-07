import json
import logging
from ine.municipios_ine_services import Municipios, normalizar_texto
from ine.rendimiento_services import RendimientosIne
from ine.uso_suelos_services import UsoSuelosIne
from ine.gemini_services import asistente_virtual

logger = logging.getLogger(__name__)


class IneAgregador:

    @staticmethod
    def obtener_analisis_completo(busqueda_municipio: str | None = None) -> dict:
        if not busqueda_municipio or not busqueda_municipio.strip():
            return {
                "estado": "error",
                "mensaje": "Por favor, introduce un código o nombre de municipio."
            }

        termino_limpio = busqueda_municipio.strip()

        try:
            servicio_municipios = Municipios()
            codigo_municipio = None
            nombre_municipio = None

            # 1. Resolver la equivalencia mediante el XLSX de la clase Municipios
            if termino_limpio.isdigit():
                codigo_municipio = termino_limpio.zfill(5)
                nombre_municipio = servicio_municipios.obtener_nombre_por_codigo(codigo_municipio) or termino_limpio
            else:
                # Búsqueda por nombre exacto en los datos cargados del XLSX
                codigo_municipio = servicio_municipios.obtener_codigo_por_nombre(termino_limpio)
                
                # Búsqueda por coincidencia parcial si el nombre no es exacto
                if not codigo_municipio:
                    servicio_municipios._cargar_datos()
                    nombre_norm_buscado = normalizar_texto(termino_limpio)
                    for nombre_norm, cod_ine in servicio_municipios._nombre_a_codigo.items():
                        if nombre_norm_buscado in nombre_norm:
                            codigo_municipio = cod_ine
                            break

                if codigo_municipio:
                    nombre_municipio = servicio_municipios.obtener_nombre_por_codigo(codigo_municipio)
                else:
                    nombre_municipio = termino_limpio

            # 2. Consultar los datos usando SIEMPRE el código INE resuelto del XLSX
            parametro_consulta = codigo_municipio or termino_limpio

            rendimiento_service = RendimientosIne()
            datos_brutos_ren = rendimiento_service.fetch(parametro_consulta)
            json_rendimientos = rendimiento_service.normalize(datos_brutos_ren)

            suelos_service = UsoSuelosIne()
            datos_brutos_sue = suelos_service.fetch(parametro_consulta)
            json_usosuelos = suelos_service.normalize(datos_brutos_sue)

            # 3. Empaquetar el contexto para la plantilla y Gemini
            codigo_provincia = codigo_municipio[:2] if codigo_municipio and len(codigo_municipio) == 5 else ""
            nombre_provincia = servicio_municipios.obtener_provincia_por_codigo(codigo_provincia) or "Desconocida"

            contexto_datos = {
                "municipio": {
                    "registros": [{
                        "codigo": codigo_municipio or "Desconocido",
                        "nombre": nombre_municipio,
                        "provincia": nombre_provincia
                    }]
                },
                "rendimientos": json_rendimientos,
                "uso_suelos": json_usosuelos
            }

            contexto_json_str = json.dumps(contexto_datos, ensure_ascii=False, indent=2)
            informe_ia = asistente_virtual(contexto_json_str)

            return {
                "estado": "exito",
                "datos": contexto_datos,
                "informe_ia": informe_ia
            }

        except Exception as e:
            logger.error(f"Error durante el proceso de agregación INE: {e}", exc_info=True)
            return {
                "estado": "error",
                "mensaje": "Ocurrió un error al procesar los datos del municipio."
            }