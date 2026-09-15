import logging #rastreo de errores
import markdown #formato en el que la ia devuelve los datos
from google import genai #cliente
from google.genai import types #contiene todas las clases de soporte, definiciones de tipos de datos, configuraciones 
#y esquemas estructurados que necesitas para interactuar con los modelos de Gemini de forma avanzada
from google.genai.errors import APIError #manejo de errores
from config.entorno import API_KEY_GEMINI #llamada a la api

logger = logging.getLogger(__name__)

# Usamos los nombres de modelos oficiales estables actuales
MODELOS_INTENTAR = ["gemini-3.6-flash", "gemini-2.5-flash"]


def _consultar_gemini(contexto_negocio: str, system_instruction: str) -> str:
    if not API_KEY_GEMINI:
        return "<p>Error: No se encontró la API Key de Gemini.</p>"

    client = genai.Client(api_key=API_KEY_GEMINI)

    prompt = (
        "Sintetiza los siguientes datos territoriales en un informe ejecutivo conciso y completo:\n\n"
        "1. **Tendencias del Mercado y Rendimiento:** (Máximo 3 viñetas con puntos clave).\n"
        "2. **Uso del Suelo y Capacidad:** (Máximo 2 viñetas sobre distribución y aprovechamiento).\n"
        "3. **Perspectivas:** (1 o 2 conclusiones directas).\n\n"
        f"Datos (JSON):\n{contexto_negocio}"
    )

    # Configuración limpia sin restricciones de thinking que corten la respuesta
    configuracion = types.GenerateContentConfig(
        system_instruction=system_instruction,
        max_output_tokens=8192,  # Margen amplio desde el inicio para evitar cortes
        temperature=0.2, #temperatura de creatividad cercano a 0 mas racional cercano a 1 mas disparatado
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

            texto_markdown = response.text if response and response.text else ""
            
            if not texto_markdown:
                logger.warning(f"El modelo {modelo} devolvió una respuesta vacía.")
                continue

            return markdown.markdown(texto_markdown)

        except APIError as e:
            logger.error(f"Error de API Gemini con {modelo}: {e}")
            continue  # probamos el siguiente modelo pase lo que pase
        except Exception as e:
            logger.error(f"Error inesperado al conectar con Gemini ({modelo}): {e}")
            continue

    return "<p>El servicio de IA está experimentando una alta demanda en este momento. Por favor, reintenta la consulta en unos segundos.</p>"


def asistente_virtual(contexto_negocio: str) -> str:
    system_instruction = (
        "Eres un analista de datos agrícolas de respuesta rápida. "
        "Debes responder SIEMPRE en español de España. "
        "Sintetiza la información de forma clara, directa y completa. "
        "Usa formato Markdown estricto (listas de viñetas con '*' y negritas con '**'). "
        "Desarrolla cada sección por completo. Nunca dejes frases ni secciones a medio terminar."
    )
    return _consultar_gemini(contexto_negocio, system_instruction)


# ¿es Castilla y León una economía en crecimiento?
def asistente_crecimiento(contexto_negocio: str) -> str:
    system_instruction = (
        "Eres un analista económico especializado en dinámicas de crecimiento regional. "
        "Debes responder SIEMPRE en español de España. "
        "Evalúa si Castilla y León muestra signos de crecimiento económico a partir de los datos. "
        "Usa formato Markdown estricto (listas de viñetas y negritas). "
        "Desarrolla cada punto por completo y no dejes respuestas inconclusas."
    )
    return _consultar_gemini(contexto_negocio, system_instruction)


# ¿ha valido la pena invertir en Castilla y León?
def asistente_financiero(contexto_negocio: str) -> str:
    system_instruction = (
        "Eres un analista financiero especializado en evaluación de inversiones territoriales. "
        "Debes responder SIEMPRE en español de España. "
        "Valora si invertir en Castilla y León ha resultado rentable según los datos. "
        "Usa formato Markdown estricto (listas de viñetas y negritas). "
        "Sé exhaustivo y completa todas las secciones."
    )
    return _consultar_gemini(contexto_negocio, system_instruction)


# ¿es sostenible el crecimiento en Castilla y León?
def asistente_desarrollo(contexto_negocio: str) -> str:
    system_instruction = (
        "Eres un analista de desarrollo territorial especializado en sostenibilidad. "
        "Debes responder SIEMPRE en español de España. "
        "Evalúa si el crecimiento de Castilla y León es sostenible en el tiempo. "
        "Usa formato Markdown estricto (listas de viñetas y negritas). "
        "Desarrolla todas las conclusiones de forma íntegra."
    )
    return _consultar_gemini(contexto_negocio, system_instruction)