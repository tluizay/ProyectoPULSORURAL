from pathlib import Path
from ine.services.orchestrator import procesar_directorio_ceas
from ine.gemini_services import asistente_virtual
from ine.analiticas.disparador import disparador_analitica  

class IneAgregador:
    @staticmethod
    def obtener_analisis_completo():
        """Método original para obtener el informe más reciente y el análisis de Gemini."""
        try:
            ruta_carpeta_pdfs = Path("ine/datos/pdfs")
            
            if not ruta_carpeta_pdfs.exists():
                return {
                    "estado": "error",
                    "mensaje": f"La carpeta de informes no existe en la ruta: {ruta_carpeta_pdfs}"
                }

            # Procesamos todos los archivos de la carpeta
            lista_todos_los_informes = procesar_directorio_ceas(ruta_carpeta_pdfs)

            if not lista_todos_los_informes:
                return {
                    "estado": "error",
                    "mensaje": "No se encontraron informes PDF procesables en la carpeta."
                }

            # Ordenamos por año de forma descendente y cogemos el más reciente
            lista_todos_los_informes.sort(key=lambda x: x.get("anio") or 0, reverse=True)
            informe_principal = lista_todos_los_informes[0]

            # Generamos el análisis inteligente con Gemini para este informe
            informe_ia = asistente_virtual(informe_principal)

            return {
                "estado": "ok",
                "datos": informe_principal,
                "todos_los_informes": lista_todos_los_informes,
                "informe_ia": informe_ia
            }

        except Exception as e:
            return {
                "estado": "error",
                "mensaje": f"Ocurrió un error al procesar los documentos: {str(e)}"
            }

    @staticmethod
    def obtener_datos_para_grafica(tipo_analitica: str):
        """Nuevo método específico para alimentar las gráficas mediante el dispatcher de analiticas/."""
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
                    "mensaje": "No se encontraron informes PDF procesables para la gráfica."
                }

            # Delegamos la transformación matemática al paquete analiticas/ usando el dispatcher
            datos_grafica = disparador_analitica(tipo_analitica, lista_todos_los_informes)

            return {
                "estado": "ok",
                "datos_grafica": datos_grafica
            }

        except Exception as e:
            return {
                "estado": "error",
                "mensaje": f"Ocurrió un error al procesar las analíticas: {str(e)}"
            }