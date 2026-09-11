from pathlib import Path
from ine.services.orchestrator import procesar_directorio_ceas
from ine.gemini_services import asistente_virtual, asistente_crecimiento, asistente_desarrollo, asistente_financiero
from ine.analiticas.disparador import disparador_analitica

class IneAgregador:

    ASISTENTES = {
        "virtual": asistente_virtual,
        "crecimiento": asistente_crecimiento,
        "financiero": asistente_financiero,
        "desarrollo": asistente_desarrollo,
    }

    @staticmethod
    def obtener_datos_base(tipo_analitica: str = "evolucion_general"):
        """
        Procesa los PDFs y devuelve los datos crudos + los datos de gráfica.
        NO llama a Gemini. Pensado para cachear en sesión en la carga inicial.
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

            lista_todos_los_informes.sort(key=lambda x: x.get("anio") or 0, reverse=True)

            datos_grafica = disparador_analitica(tipo_analitica, lista_todos_los_informes)

            return {
                "estado": "ok",
                "datos": lista_todos_los_informes,
                "panel_completo": lista_todos_los_informes,
                "datos_grafica": datos_grafica,
            }

        except Exception as e:
            return {
                "estado": "error",
                "mensaje": f"Ocurrió un error al procesar los documentos: {str(e)}"
            }

    @staticmethod
    def generar_informe_ia(tipo_informe: str, lista_informes: list):
        """
        Llama a UN solo asistente de Gemini, el que el usuario haya elegido.
        Requiere la lista de informes ya procesada (de obtener_datos_base).
        """
        asistente = IneAgregador.ASISTENTES.get(tipo_informe)

        if asistente is None:
            return {
                "estado": "error",
                "mensaje": f"Tipo de informe no reconocido: '{tipo_informe}'"
            }

        try:
            texto_html = asistente(lista_informes)
            return {"estado": "ok", "informe_ia": texto_html, "tipo": tipo_informe}
        except Exception as e:
            return {
                "estado": "error",
                "mensaje": f"Ocurrió un error al generar el informe con IA: {str(e)}"
            }