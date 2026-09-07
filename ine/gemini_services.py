from google import genai
from google.genai import types
from config.entorno import API_KEY_GEMINI


def asistente_virtual(contexto_negocio):
    if not API_KEY_GEMINI:
        return {"error": "No se encontró la API Key de Gemini."}

    try:
        client = genai.Client(api_key=API_KEY_GEMINI)

        system_instruction = ( "Eres un estadista, interprete de datos de mercado agricola y el uso de suelos de tierra de cultivo."
                              "Estas enfocado en la bsuqueda de tendencias, patrones y observaciones en el ambito agricola."
        
        )

        prompt = (
            "Analiza los siguientes datos económicos y proporciona un analisis critico:\n"
            "1. Tendencias del mercado: \n"
            "2. Capacidad de retorno de la inversión.\n"
            "3. Situación de la industria.\n\n"
            f"Datos (JSON):\n{contexto_negocio}"
        )

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",  # ← más rápido, sin razonamiento largo
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