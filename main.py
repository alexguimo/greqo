from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

API_TOKEN = os.getenv("API_TOKEN")

class Comando(BaseModel):
    texto: str

@app.get("/")
def home():
    return {"mensaje": "Greqo activo 🚀"}

@app.post("/comando")
def procesar(data: Comando, authorization: str = Header(None)):

    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="No autorizado")

    texto = data.texto.lower()

    if "llama" in texto:
        return {"accion": "llamar", "contacto": "mamá"}

    if "abre whatsapp" in texto:
        return {"accion": "abrir_app", "app": "com.whatsapp"}

    return {
        "accion": "hablar",
        "respuesta": "No entendí, repite por favor."
    }
