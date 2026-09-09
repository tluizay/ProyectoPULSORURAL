import json
from django.core.cache import cache
from aemet.aemet_services import Aemet  
from aemet.gemini_services import asistente_virtual  

class ClimaInteligenteAggregator:
    
    @staticmethod
    def obtener_analisis_completo(identificador_estacion: str = None, latitud: float = 0.0, longitud: float = 0.0, anio: int = None, mes: int = None, forzar_regeneracion: bool = False):
        """
        Donde los datos de gemini y aemet convergen con soporte de caché.
        """
        # Si no se pasan año y mes, usamos los actual por defecto
        from datetime import datetime
        anio = anio or datetime.now().year
        mes = mes or datetime.now().month
        
        # 1. Construir una clave de caché única y robusta
        # Usamos un identificador por defecto si no viene estación ni coordenadas
        id_cache_base = identificador_estacion or f"lat_{latitud}_lon_{longitud}"
        clave_cache = f"clima_inteligente_{id_cache_base}_{anio}_{mes}"
        
        # 2. Verificar si existe en caché y no se fuerza la regeneración
        if not forzar_regeneracion:
            datos_en_cache = cache.get(clave_cache)
            if datos_en_cache:
                # Opcional: puedes añadir un indicador de que vino de caché
                datos_en_cache["origen_cache"] = True
                return datos_en_cache

        # 3. Si no está en caché (o se fuerza), ejecutamos la lógica habitual
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
        
        # 4. Guardar en caché (por ejemplo, durante 4 horas = 14400 segundos)
        # Puedes ajustar el tiempo según convenga
        cache.set(clave_cache, resultado, timeout=14400)
        
        return resultado