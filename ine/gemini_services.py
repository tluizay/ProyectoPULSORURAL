import logging
import markdown
from google import genai
from google.genai import types
from google.genai.errors import APIError
from config.entorno import API_KEY_GEMINI

logger = logging.getLogger(__name__)


def asistente_virtual(contexto_negocio: str) -> str:
    if not API_KEY_GEMINI:
        return "<p>Error: No se encontró la API Key de Gemini.</p>"

    client = genai.Client(api_key=API_KEY_GEMINI)

    system_instruction = (
        "Eres un analista de datos agrícolas de respuesta rápida. "
        "Debes responder SIEMPRE en español de España. "
        "Sintetiza la información de forma clara, directa y completa. "
        "Usa formato Markdown (listas de viñetas y negritas). "
        "Nunca dejes frases ni secciones a medio terminar."
    )

    prompt = (
        "Sintetiza los siguientes datos territoriales en un informe ejecutivo conciso:\n\n"
        "1. **Tendencias del Mercado y Rendimiento:** (Máximo 3 viñetas con puntos clave).\n"
        "2. **Uso del Suelo y Capacidad:** (Máximo 2 viñetas sobre distribución y aprovechamiento).\n"
        "3. **Perspectivas:** (1 o 2 conclusiones directas).\n\n"
        f"Datos (JSON):\n{contexto_negocio}"
    )

    configuracion = types.GenerateContentConfig(
        system_instruction=system_instruction,
        max_output_tokens=2000,
        temperature=0.2,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    )

   
    modelos_intentar = ["gemini-3.5-flash", "gemini-3.5-flash-lite"]

    for modelo in modelos_intentar:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=prompt,
                config=configuracion,
            )

            texto_markdown = response.text or "No se pudo generar el informe."
            return markdown.markdown(texto_markdown)

        except APIError as e:
        
            if e.code == 503 or "503" in str(e):
                logger.warning(
                    f"Modelo {modelo} saturado (503). Intentando fallback..."
                )
                continue
            logger.error(f"Error de API Gemini con {modelo}: {e}")
            break
        except Exception as e:
            logger.error(f"Error inesperado al conectar con Gemini: {e}")
            break

    return "<p>El servicio de IA está experimentando una alta demanda en este momento. Por favor, reintenta la consulta en unos segundos.</p>"