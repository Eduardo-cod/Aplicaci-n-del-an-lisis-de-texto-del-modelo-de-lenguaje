#Deteccion de opiniones, tono, problemas de seguridad y contenido confidencial
#AZURE AI LANGUAJE - ENFOCADO EN FOUNDRY TOOLs
import json
import os

from dotenv import load_dotenv

load_dotenv()
#LLAMANDO LAS CREDENCIALES DE AZURE LANGUAGE TOOLS
AI_KEY = os.getenv("AZURE_AI_KEY")
AI_SERVICES_ENDPOINT = os.getenv("AI_SERVICES_ENDPOINT")
#LLAMANDO LAS CREDENCIALES DE AZURE OPEN AI
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_VERSION = os.getenv("API_VERSION")
OPENAPI_NAME_CHAT_DEPLOYMENT = os.getenv("DEPLOYMENT_NAME")

def titulo(texto):
    """Imprime un encabezado en consola"""
    print("\n" + "=" * 70 + f"\n  {texto}\n" + "=" * 70)

def get_language_client():
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    return TextAnalyticsClient(AI_SERVICES_ENDPOINT, AzureKeyCredential(AI_KEY))

def get_opeai_client(api_version=None):
    from openai import AzureOpenAI
    return AzureOpenAI(azure_endpoint=OPENAI_ENDPOINT, api_key=AI_KEY, api_version=api_version or OPENAI_API_VERSION)


TEXTO = """El pasado 3 de marzo, Laura Gomez, gerente de compras de Grupo Andino en Bogota,
envio un correo a Contoso Ltda. para reportar que el pedido 4587 de 120 laptops llego con
2 semanas de retraso y 15 equipos danados. Solicita un reembolso de 18.000 USD o el reemplazo
inmediato antes del 30 de abril, de lo contrario cancelara el contrato anual."""

#PARTE A RECONOCIMIENTO DE ENTIDADES NER
def parte_A_language():
    titulo("A) RECONOCIMIENTO DE ENTIDADES NER")
    client = get_language_client()

    ner = client.recognize_entities([TEXTO], language="es")[0]
    print("Entidades reconocidas")
    print(f"{"ENTIDAD"} - {"CATEGORIA"} - {"NIVEL DE CONFIANZA"}")
    for e in ner.entities:
        print(f"{e.text} - {e.category} - {e.confidence_score}")

    #FRASES CLAVE
    titulo("B) FRASES CLAVE")
    kp = client.extract_key_phrases([TEXTO], language="es")[0]
    print("\nFrases clave (temas):", ", ".join(kp.key_phrases))

    #GENERAR RESUMEN
    titulo("C) GENERAR RESUMEN")
    resumen = client.begin_abstract_summary([TEXTO], language="es", sentence_count=2)
    for doc in resumen.result():
        print("\nResumen abstractivo:", " ".join(s.text for s in doc.summaries))

#PARTE B SOLCIITUD GENERATIVA CON SALIDAS JSON ESTRUCTURAS
ESQUEMA = {
    "name": "analisis_correo",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "resumen": {"type": "string", "description": "Maximo 2 frases"},
            "temas": {"type": "array", "items": {"type": "string"}},
            "entidades": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "texto": {"type": "string"},
                        "tipo": {"type": "string",
                                 "enum": ["PERSONA", "ORGANIZACION", "LUGAR", "FECHA",
                                          "PRODUCTO", "CANTIDAD", "IDENTIFICADOR", "OTRO"]},
                    },
                    "required": ["texto", "tipo"],
                    "additionalProperties": False,
                },
            },
            "intencion": {"type": "string",
                          "enum": ["queja", "consulta", "compra", "cancelacion", "otro"]},
            "urgencia": {"type": "string", "enum": ["baja", "media", "alta"]},
        },
        "required": ["resumen", "temas", "entidades", "intencion", "urgencia"],
        "additionalProperties": False,
    },
}

def parte_B_generativa():
    titulo("B) SOLICITUD JSON ESTRUCTURADO GENERATIVO")
    client = get_opeai_client()

    respuesta = client.chat.completions.create(
        model=OPENAPI_NAME_CHAT_DEPLOYMENT,
        temperature=0,
        messages=[
            {"role" : "system", "content": "Eres un analista de atencion al cliente. Extrae informacion SOLO del texto dado sin inventar datos."},
            {"role" : "user", "content": TEXTO},
        ],
        response_format={"type": "json_schema", "json_schema" : ESQUEMA }, 
    )
    # CONVERTIMOS LA RESPUESTA EN STRING JSON VALIDO
    datos = json.loads(respuesta.choices[0].message.content)
    print("************")
    print(datos)
    print("************")
    print(json.dumps(datos, indent=2, ensure_ascii=False))

    #usabilidad
    print(f"Token de entrada: {respuesta.usage.prompt_tokens}")
    print(f"Token de salida: {respuesta.usage.completion_tokens}")


if __name__ == "__main__":
    parte_A_language()
    parte_B_generativa()


