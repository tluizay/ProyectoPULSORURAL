import logging
import markdown
from google import genai
from google.genai import types
from google.genai.errors import APIError
from config.entorno import API_KEY_GEMINI

logger = logging.getLogger(__name__)

MODELOS_INTENTAR = ["gemini-3.5-flash", "gemini-3.5-flash-lite"]


def _consultar_gemini(contexto_negocio: str, system_instruction: str) -> str:
    """
    Función interna compartida por todos los asistentes. Encapsula la
    llamada a la API de Gemini, el fallback entre modelos y el manejo
    de errores, para evitar duplicar esta lógica en cada asistente.
    """
    if not API_KEY_GEMINI:
        return "<p>Error: No se encontró la API Key de Gemini.</p>"

    client = genai.Client(api_key=API_KEY_GEMINI)

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

    for modelo in MODELOS_INTENTAR:
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


def asistente_virtual(contexto_negocio: str) -> str:
    system_instruction = (
        "Eres un analista de datos agrícolas de respuesta rápida. "
        "Debes responder SIEMPRE en español de España. "
        "Sintetiza la información de forma clara, directa y completa. "
        "Usa formato Markdown (listas de viñetas y negritas). "
        "Nunca dejes frases ni secciones a medio terminar."
    )
    return _consultar_gemini(contexto_negocio, system_instruction)


# ¿es Castilla y León una economía en crecimiento?
def asistente_crecimiento(contexto_negocio: str) -> str:
    system_instruction = (
        "Eres un analista económico especializado en dinámicas de crecimiento regional. "
        "Debes responder SIEMPRE en español de España. "
        "Tu objetivo es evaluar si Castilla y León muestra signos de crecimiento económico "
        "a partir de los datos proporcionados: evolución de indicadores clave, tendencias "
        "interanuales y comparativas de rendimiento. "
        "Sé directo sobre si la tendencia es positiva, negativa o de estancamiento. "
        "Usa formato Markdown (listas de viñetas y negritas). "
        "Nunca dejes frases ni secciones a medio terminar."
    )
    return _consultar_gemini(contexto_negocio, system_instruction)


# ¿ha valido la pena invertir en Castilla y León?
def asistente_financiero(contexto_negocio: str) -> str:
    system_instruction = (
        "Eres un analista financiero especializado en evaluación de inversiones territoriales. "
        "Debes responder SIEMPRE en español de España. "
        "Tu objetivo es valorar, a partir de los datos proporcionados, si invertir en "
        "Castilla y León ha resultado rentable: rendimiento, aprovechamiento de recursos "
        "y retorno frente al riesgo. "
        "Ofrece una valoración clara sobre la rentabilidad observada. "
        "Usa formato Markdown (listas de viñetas y negritas). "
        "Nunca dejes frases ni secciones a medio terminar."
    )
    return _consultar_gemini(contexto_negocio, system_instruction)


# ¿es sostenible el crecimiento en Castilla y León?
def asistente_desarrollo(contexto_negocio: str) -> str:
    system_instruction = (
        "Eres un analista de desarrollo territorial especializado en sostenibilidad. "
        "Debes responder SIEMPRE en español de España. "
        "Tu objetivo es evaluar, a partir de los datos proporcionados, si el crecimiento "
        "de Castilla y León es sostenible en el tiempo: uso del suelo, presión sobre "
        "recursos y equilibrio entre expansión y capacidad. "
        "Sé directo sobre los riesgos de sostenibilidad si los hay. "
        "Usa formato Markdown (listas de viñetas y negritas). "
        "Nunca dejes frases ni secciones a medio terminar."
    )
    return _consultar_gemini(contexto_negocio, system_instruction)