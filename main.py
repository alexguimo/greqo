from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from openai import OpenAI
import os
import random
import requests


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

    contexto = "\n".join(memoria_usuario[-5:])

    prompt = PERSONALIDAD + "\n\nContexto:\n" + contexto + "\nUsuario: " + texto_usuario

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi",
                "prompt": prompt,
                "stream": False
            }
        )

        data = response.json()

        return data["response"]

    except Exception as e:
        print("Error Ollama:", e)
        return "Estoy teniendo problemas para procesar eso ahora mismo."


@app.get("/")
def inicio():
    return {"mensaje": "Greqo activo 🚀"}

def necesita_ia(texto):
    palabras_clave = ["explica", "por qué", "cómo", "opina", "analiza"]
    return any(p in texto for p in palabras_clave)


def respuesta_simple(texto):
    if "hora" in texto:
        return "No tengo acceso al tiempo real aún."
    
    if "nombre" in texto:
        return "Soy Greqo."
    
    return "Continúa, estoy escuchando."


@app.post("/comando")
def procesar(data: Comando, credenciales: HTTPAuthorizationCredentials = Depends(security)):
    
    if credenciales.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="No autorizado")

    texto = data.texto.lower()

    # 🥇 FILTRO BASICO (ahorro máximo)
    if len(texto) < 5:
        return {
            "accion": "hablar",
            "respuesta": "No entendí bien, repite."
        }

    # 🥇 RESPUESTAS GRATIS
    if "hola" in texto:
        return {"accion": "hablar", "respuesta": "Hola. Soy Greqo."}

    if "cómo estás" in texto:
        return {"accion": "hablar", "respuesta": "Operando correctamente."}

    # 🥈 MEMORIA SIMPLE
    if texto in memoria_usuario:
        return {
            "accion": "hablar",
            "respuesta": "Ya hemos hablado de eso antes."
        }

    # 🥉 DECISIÓN INTELIGENTE (AQUÍ ESTÁ EL AHORRO REAL)
    if necesita_ia(texto):
        respuesta = generar_respuesta(texto)
    else:
        respuesta = respuesta_simple(texto)

    return {
        "accion": "hablar",
        "respuesta": respuesta
    }
