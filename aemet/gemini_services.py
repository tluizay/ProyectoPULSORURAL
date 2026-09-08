from google import genai
from google.genai import types
from config.entorno import API_KEY_GEMINI


def asistente_virtual(contexto_negocio):
    if not API_KEY_GEMINI:
        return {"error": "No se encontró la API Key de Gemini."}

    try:
        client = genai.Client(api_key=API_KEY_GEMINI)

        system_instruction = (
            "Eres un experto agrónomo especializado en el clima y la agricultura de Castilla y León. "
            "Tu objetivo es interpretar datos meteorológicos reales y contextualizarlos a un entorno agrícola "
            "para evaluar las condiciones agronómicas, detectar posibles riesgos de estrés térmico, sequía o heladas, "
            "y ofrecer un análisis claro y útil para la planificación agrícola. "
            "Ignora los datos que no tenemos, solo en base a los que tenemos. "
            "Sé conciso: máximo 150 palabras."
        )

        prompt = (
            "Analiza los siguientes datos meteorológicos y proporciona un informe agronómico estructurado:\n"
            "1. Comportamiento térmico y riesgos.\n"
            "2. Precipitaciones: evolución y suficiencia.\n"
            "3. Conclusión sobre impacto en campañas agrícolas.\n\n"
            f"Datos (JSON):\n{contexto_negocio}"
        )

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite", 
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=512,       # ← limita la respuesta
                temperature=0.3,
            ),
        )

        return {"interpretacion_ia": response.text}

    except Exception as e:
        return {"error": f"Error al conectar con Gemini: {str(e)}"}   