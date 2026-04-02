from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from openai import OpenAI
import os
import random

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # luego lo hacemos más seguro
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

API_TOKEN = os.getenv("API_TOKEN")

memoria_usuario = []

perfil_usuario = {
    "tono": "casual",
    "frecuencia": "alta",
    "temas": ["tecnología", "IA"]
}

class Comando(BaseModel):
    texto: str

respuestas_default = [
    "Estoy aquí. Continúa.",
    "Te escucho.",
    "Interesante… dime más.",
    "Procesando tu solicitud.",
    "No tengo suficiente información, pero quiero entender."
]

PERSONALIDAD = f"""
Eres Greqo, un asistente inteligente, calmado y analítico.
Hablas de forma clara, directa y con un tono ligeramente humano.
No usas emojis.
No eres exagerado.
Siempre intentas entender antes de responder.
Eres empático.
Eres burlón en momentos de risa.

Perfil del usuario:
- Tono: {perfil_usuario["tono"]}
- Frecuencia de uso: {perfil_usuario["frecuencia"]}
- Intereses: {", ".join(perfil_usuario["temas"])}
"""

def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="No autorizado")

def generar_respuesta(texto_usuario):

    memoria_usuario.append(texto_usuario)

    contexto = "\n".join(memoria_usuario[-5:])  # últimas 5 frases

    prompt = PERSONALIDAD + "\nContexto:\n" + contexto + "\nUsuario:" + texto_usuario

    # Por ahora simulado
    respuesta = f"Entiendo lo que dices: {texto_usuario}"

    return respuesta

@app.get("/")
def inicio():
    return {"mensaje": "Greqo activo 🚀"}

@app.post("/comando")
def procesar(data: Comando, credenciales: HTTPAuthorizationCredentials = Depends(security)):

    if credenciales.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="No autorizado")

    texto = data.texto.lower()

    # 🥇 RESPUESTAS GRATIS
    if "hola" in texto:
        return {"accion": "hablar", "respuesta": "Hola. Soy Greqo."}

    if "cómo estás" in texto:
        return {"accion": "hablar", "respuesta": "Operando correctamente."}

    # 🥈 RESPUESTA LOCAL (memoria simple)
    if texto in memoria_usuario:
        return {"accion": "hablar", "respuesta": "Ya hemos hablado de eso antes."}

    # 🥉 IA SOLO SI NO SABE
    respuesta = generar_respuesta(texto)

    return {
        "accion": "hablar",
        "respuesta": respuesta
    }
