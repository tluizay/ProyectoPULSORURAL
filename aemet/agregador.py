import json
from django.core.cache import cache
from aemet.aemet_services import Aemet  
from aemet.gemini_services import asistente_virtual  
from datetime import datetime

class ClimaInteligenteAggregator:
    
    @staticmethod
    def obtener_analisis_completo(identificador_estacion: str = None, latitud: float = 0.0, longitud: float = 0.0, anio: int = None, mes: int = None, forzar_regeneracion: bool = False):

        
        anio = anio or datetime.now().year
        mes = mes or datetime.now().month
        
        id_cache_base = identificador_estacion or f"lat_{latitud}_lon_{longitud}"
        clave_cache = f"clima_inteligente_{id_cache_base}_{anio}_{mes}"

        if not forzar_regeneracion:
            datos_en_cache = cache.get(clave_cache)
            if datos_en_cache:
                datos_en_cache["origen_cache"] = True
                return datos_en_cache

        cliente_aemet = Aemet(identificador_estacion=identificador_estacion)
        datos_brutos = cliente_aemet.fetch(latitud=latitud, longitud=longitud)
        json_aemet = cliente_aemet.normalize(datos_brutos)
        
        if not json_aemet.get("registros"):
            return {
                "estado": "error",
                "mensaje": "No se encontraron registros meteorológicos válidos para analizar."
            }
            
        contexto_json_str = json.dumps(json_aemet, ensure_ascii=False)
        informe_ia = asistente_virtual(contexto_json_str)
        
        resultado = {
            "estado": "exitoso",
            "estacion": json_aemet.get("estacion", "Desconocida"),
            "fuente_datos": json_aemet.get("fuente", "AEMET"),
            "datos_meteorologicos": json_aemet["registros"],
            "interpretacion_ia": informe_ia,
            "anio": anio,
            "mes": mes,
            "origen_cache": False
        }
        
        cache.set(clave_cache, resultado, timeout=14400)
        
        return resultado