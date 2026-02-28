from mcp.server.fastmcp import FastMCP
from typing import Literal
from openai import AzureOpenAI
import os
import json

# Inicialización del servidor MCP
mcp = FastMCP("SportIA1")
DB_PATH = "e:/python/Modulo 5/SportIA1/datos_entreno.json"

# CONFIGURACIÓN DE AZURE
client = AzureOpenAI(
    azure_endpoint="https://khipusaigpt0566189501.services.ai.azure.com",
    api_key=os.getenv("AZURE_OPENAI_KEY"), # Leemos la llave de forma segura
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
    """Chat inteligente con Azure OpenAI. Incluye historial para contexto real."""
    try:
        historial_contexto = ""
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "r", encoding="utf-8") as f:
                datos = json.load(f)
                resumen = datos.get("historial", [])[-3:]
                historial_contexto = f"\nDatos recientes de Bruno: {resumen}"

        # Llamada a Azure
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "Eres un entrenador experto de SportIA. Responde breve y técnico."},
                {"role": "user", "content": f"{historial_contexto}\nPregunta: {pregunta}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        # Si falla Azure, devolvemos el error pero el servidor no se cae
        return f"Error de conexión con Azure: {str(e)}"

if __name__ == "__main__":
    mcp.run()