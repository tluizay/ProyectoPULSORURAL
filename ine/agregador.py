from pathlib import Path
from ine.services.orchestrator import procesar_directorio_ceas
from ine.gemini_services import asistente_virtual
from ine.analiticas.disparador import disparador_analitica  

class IneAgregador:
    @staticmethod
    def obtener_todo_unificado(tipo_analitica: str = "evolucion_general"):
        """
        Método unificado que procesa los PDFs una sola vez y devuelve 
        tanto los datos para las gráficas como el análisis de Gemini.
        """
        try:
            ruta_carpeta_pdfs = Path("ine/datos/pdfs")
            
            if not ruta_carpeta_pdfs.exists():
                return {
                    "estado": "error",
                    "mensaje": f"La carpeta de informes no existe en la ruta: {ruta_carpeta_pdfs}"
                }

            lista_todos_los_informes = procesar_directorio_ceas(ruta_carpeta_pdfs)

            if not lista_todos_los_informes:
                return {
                    "estado": "error",
                    "mensaje": "No se encontraron informes PDF procesables en la carpeta."
                }

            # 1. Preparar datos para el asistente virtual (informe más reciente)
            lista_todos_los_informes.sort(key=lambda x: x.get("anio") or 0, reverse=True)
            informe_principal = lista_todos_los_informes[0]
            
            informe_ia = asistente_virtual(informe_principal)
            print("DEBUG - Resultado de la IA:", informe_ia)

            # 2. Obtener datos para las gráficas usando el disparador
            datos_grafica = disparador_analitica(tipo_analitica, lista_todos_los_informes)

            return {
                "estado": "ok",
                "datos": informe_principal,
                "panel_completo": lista_todos_los_informes,
                "informe_ia": informe_ia,
                "datos_grafica": datos_grafica
            }

        except Exception as e:
            return {
                "estado": "error",
                "mensaje": f"Ocurrió un error al procesar los documentos: {str(e)}"
            }