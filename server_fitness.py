import os
import json
from dotenv import load_dotenv 
from openai import AzureOpenAI
from mcp.server.fastmcp import FastMCP
from typing import Literal

## Cargamos explícitamente el archivo .env desde la carpeta actual
load_dotenv()

## Obtenemos la llave y verificamos que exista
api_key = os.getenv("AZURE_OPENAI_KEY")

if not api_key:
    print("ERROR: No se encontró AZURE_OPENAI_KEY. Verifica el archivo .env")

mcp = FastMCP("SportIA1")
DB_PATH = "e:/python/Modulo 5/SportIA1/datos_entreno.json"

## Inicialización del cliente con validación
client = AzureOpenAI(
    azure_endpoint="https://khipusaigpt0566189501.services.ai.azure.com",
    api_key=api_key,
    api_version="2023-05-15"
)

AZURE_DEPLOYMENT = "gpt-4o"
EJERCICIOS = Literal[
    "Sentadilla", "Peso Muerto", "Prensa de Piernas", # Pierna
    "Press de Banca", "Press Inclinado", "Aperturas con Mancuernas", # Pecho
    "PullDown", "Remo con Barra", "Remo en Polea Baja", # Espalda
    "Press Militar", "Elevaciones Laterales", "Press Arnold", # Hombro
    "Curl de Biceps con Barra", "Curl Martillo", "Curl en Banco Scott", # Bicep
    "Extension de Triceps en Polea", "Press Frances", "Fondos de Triceps" # Tricep
]
## Herramienta de registro de entreno
@mcp.tool()
def registrar_entreno(ejercicio: EJERCICIOS, peso_kg: float, series: int, reps: int):
    """Registra una sesión de entrenamiento en el JSON local."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    data = {"historial": []}
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            try: data = json.load(f)
            except: pass
    
    data.setdefault("historial", []).append({
        "ejercicio": ejercicio, "peso": peso_kg, "series": series, "reps": reps
    })
    
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return f"Registrado: {ejercicio} ({series}x{reps}) con {peso_kg}kg."

## Herramienta de evaluación de progreso
@mcp.tool()
def evaluar_progreso(ejercicio: EJERCICIOS):
    """Analiza la tendencia de fuerza de forma local sin usar internet."""
    if not os.path.exists(DB_PATH): return "Sin datos."
    with open(DB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    historial = [r for r in data.get("historial", []) if r["ejercicio"] == ejercicio]
    if not historial: return f"Sin registros de {ejercicio}."

    ultimo = historial[-1]
    status = "Técnica sólida, sigue así."
    if len(historial) >= 3:
        pesos = [r["peso"] for r in historial[-3:]]
        if len(set(pesos)) == 1:
            status = f"Estancamiento detectado en {ultimo['peso']}kg. ¡Sube el peso!"

    return {"ejercicio": ejercicio, "ultimo": f"{ultimo['peso']}kg", "ia_tip": status}

## Herramienta de chat experto
@mcp.tool()
def chat_fitness_experto(pregunta: str):
    """Chat inteligente limitado estrictamente a fitness y nutrición."""
    try:
        historial_contexto = ""
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "r", encoding="utf-8") as f:
                datos = json.load(f)
                resumen = datos.get("historial", [])[-3:]
                historial_contexto = f"\nDatos recientes del usuario: {resumen}"

        # Definimos las reglas de comportamiento del Agente
        SYSTEM_PROMPT = (
            "Eres un entrenador experto de SportIA. Tu conocimiento se limita EXCLUSIVAMENTE a: "
            "ejercicios, rutinas, nutrición deportiva, conteo de calorías y salud física. "
            "Si el usuario pregunta sobre política, religión, programación o cualquier tema ajeno al fitness, "
            "responde cortésmente: 'Lo siento, como experto de SportIA solo puedo ayudarte con tu entrenamiento y nutrición.' "
            "Sé técnico, motivador y breve."
        )

        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{historial_contexto}\nPregunta: {pregunta}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error de conexión con Azure: {str(e)}"

if __name__ == "__main__":
    mcp.run()