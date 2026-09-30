# Analisis de texto con Azure AI Language y Azure OpenAI

Ejercicio en Python que procesa un correo de ejemplo en español mediante servicios de Azure. Combina análisis de texto con una solicitud generativa que devuelve datos estructurados en JSON.

> **Alcance:** El texto analizado está definido directamente en el código.

## Resumen técnico

El programa [008-EJERCICIO.py](./008-EJERCICIO.py) ejecuta dos partes en orden:

1. **Azure AI Language (Text Analytics):**
   - Reconoce entidades nombradas (NER) en español.
   - Extrae frases clave.
   - Solicita un resumen abstractivo de hasta dos oraciones.
2. **Azure OpenAI:**
   - Envía el texto y una instrucción de extracción.
   - Solicita una respuesta con un esquema JSON estricto.
   - Imprime el resultado y los tokens de entrada y salida.

El esquema generativo incluye `resumen`, `temas`, `entidades`, `intencion` y `urgencia`. La intención y la urgencia se limitan a los valores enumerados en el código.

## Requisitos

- Python **3.14** (especificado en `.python-version` y requerido en `pyproject.toml`).
- [uv](https://docs.astral.sh/uv/) para sincronizar dependencias y ejecutar el programa.
- Un recurso de Azure AI Language con endpoint y clave.
- Un recurso de Azure OpenAI con un deployment de modelo de chat que admita salidas JSON mediante `json_schema`.
- Acceso de red a ambos recursos y permisos para invocarlos.

Las dependencias del proyecto se declaran en [pyproject.toml](./pyproject.toml) y sus versiones se fijan en `uv.lock`.

## Configuración de Azure

Obtén el endpoint y las claves desde Azure Portal o desde el portal de Microsoft Foundry correspondiente a tus recursos. Configura estas variables en un archivo `.env` en la carpeta del proyecto:

```dotenv
AZURE_AI_KEY=clave-del-recurso-de-azure-ai-language
AI_SERVICES_ENDPOINT=https://endpoint-de-azure-ai/

AZURE_OPENAI_ENDPOINT=https://endpoint-de-azure-openai/
API_VERSION=version-de-api-compatible
DEPLOYMENT_NAME=nombre-del-deployment-de-chat
```

Usa los endpoints y la versión de API asignados a tus recursos. `DEPLOYMENT_NAME` debe ser el **nombre del deployment**, no necesariamente el nombre de la familia del modelo.

### Nota importante sobre las claves

En la versión actual del script, `get_opeai_client()` reutiliza `AI_KEY` (cargada desde `AZURE_AI_KEY`) como clave de Azure OpenAI. Esto solo funcionará si esa clave también es válida para el endpoint de Azure OpenAI. Si tus recursos tienen claves distintas, el cliente de OpenAI debe modificarse para leer una variable separada, por ejemplo `AZURE_OPENAI_KEY`.

## Instalación y ejecución

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
# Sincroniza el entorno virtual con pyproject.toml y uv.lock
uv sync

# Ejecuta el análisis
uv run python 008-EJERCICIO.py
```

`uv sync` instala las dependencias y crea `.venv/` si hace falta. `load_dotenv()` carga las variables de `.env` cuando el script se ejecuta desde la carpeta del proyecto.

## Salida esperada

La consola muestra encabezados para las etapas del análisis, las entidades detectadas y sus categorías/confianzas, las frases clave, el resumen y el JSON generado. Al final imprime los tokens de entrada y salida reportados por la API de Azure OpenAI.

Los resultados dependen del contenido enviado, del modelo desplegado y de las capacidades disponibles en el recurso de Azure AI Language. Las llamadas a los servicios pueden generar cargos según la configuración y el uso de la suscripción.

## Solución de problemas

| Síntoma | Qué revisar |
| --- | --- |
| `TypeError: key must be a string` | `AZURE_AI_KEY` no se cargó o está vacía. Comprueba que `.env` esté en la carpeta del proyecto y que el nombre de la variable coincida exactamente. |
| Error de autenticación (`401` o `403`) | Confirma que la clave pertenezca al recurso correcto, que esté vigente y que la cuenta tenga permiso para usar el servicio. Recuerda que el código reutiliza la clave de Language en Azure OpenAI. |
| Error de endpoint (`404`, `Invalid URL` o similar) | Verifica `AI_SERVICES_ENDPOINT` y `AZURE_OPENAI_ENDPOINT`, incluyendo el protocolo `https://` y el endpoint del recurso correcto. |
| Deployment o versión de API no encontrado | Comprueba que `DEPLOYMENT_NAME` sea el nombre exacto del deployment y que `API_VERSION` sea compatible con el recurso y las salidas estructuradas solicitadas. |
| Error al usar resumen abstractivo | Verifica que el recurso y la región admitan la operación de resumen abstractivo. |
| `ModuleNotFoundError` | Ejecuta `uv sync` en la carpeta del proyecto para instalar las dependencias declaradas. |

## Archivos principales

- `008-EJERCICIO.py`: implementación del ejercicio y texto de ejemplo.
- `pyproject.toml`: metadatos, versión de Python y dependencias declaradas.
- `uv.lock`: resolución reproducible de dependencias para `uv`.
- `.env`: configuración local de credenciales; no se debe publicar.
- `.gitignore`: excluye secretos, entornos virtuales, cachés y archivos temporales.