from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
import random

app = FastAPI()
API_TOKEN = os.getenv("API_TOKEN")

class Comando(BaseModel):
    texto: str

respuestas_default = [
    "Estoy aquí. Continúa.",
    "Te escucho.",
    "Interesante… dime más.",
    "Procesando tu solicitud.",
    "No tengo suficiente información, pero quiero entender."
]

@app.get("/")
def inicio():
    return {"mensaje": "Greqo activo 🚀"}
    
@app.post("/comando")
def procesar(data: Comando, authorization: str = Header(None)):

    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="No autorizado")

    texto = data.texto.lower()

    # Respuestas con personalidad básica
    if "hola" in texto:
        return {"accion": "hablar", "respuesta": "Hola. Soy Greqo. Estoy listo."}

    if "quién eres" in texto:
        return {"accion": "hablar", "respuesta": "Soy Greqo. Un sistema diseñado para asistirte y evolucionar contigo."}

    if "cómo estás" in texto:
        return {"accion": "hablar", "respuesta": "Operando dentro de parámetros normales."}

    # Respuesta dinámica
    return {
        "accion": "hablar",
        "respuesta": random.choice(respuestas_default)
    }
