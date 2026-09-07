from google import genai
from google.genai import types
from config.entorno import API_KEY_GEMINI


def asistente_virtual(contexto_negocio):
    if not API_KEY_GEMINI:
        return {"error": "No se encontró la API Key de Gemini."}

    try:
        client = genai.Client(api_key=API_KEY_GEMINI)

        system_instruction = (
            "Eres un experto edafólogo y agrónomo especializado en los suelos de Castilla y León. "
            "Tu objetivo es interpretar los datos de suelo e indicadores geográficos proporcionados "
            "(provincia, municipio y atributos de suelo del visor ITACYL) y contextualizarlos para el sector agrícola. "
            "Evalúa la aptitud del terreno, sus características edáficas y posibles limitaciones para los cultivos. "
            "Ignora las claves con valores nulos o datos que no existan en el JSON. "
            "Sé conciso: máximo 150 palabras."
        )

        prompt = (
            "Analiza los siguientes datos edafológicos del suelo y proporciona un informe agronómico estructurado:\n"
            "1. Ubicación y características principales del suelo.\n"
            "2. Aptitud agrícola, drenaje y posibles limitaciones del terreno.\n"
            "3. Recomendaciones de manejo o cultivos idóneos.\n\n"
            f"Datos (JSON):\n{contexto_negocio}"
        )

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                max_output_tokens=512,
                temperature=0.3,
            ),
        )

        return {"interpretacion_ia": response.text}

    except Exception as e:
        return {"error": f"Error al conectar con Gemini: {str(e)}"}