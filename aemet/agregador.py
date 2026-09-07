import json
from aemet.aemet_services import Aemet  # O tu ruta de la clase Aemet
from aemet.gemini_services import asistente_virtual  # Tu función de Gemini

class ClimaInteligenteAggregator:
    
    @staticmethod
    def obtener_analisis_completo(identificador_estacion: str = None, latitud: float = 0.0, longitud: float = 0.0):
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
        
        return {
            "estado": "exitoso",
            "estacion": json_aemet["estacion"],
            "fuente_datos": json_aemet["fuente"],
            "datos_meteorologicos": json_aemet["registros"],
            "interpretacion_ia": informe_ia
        }