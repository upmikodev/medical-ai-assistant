# main.py

from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
import shutil
import datetime
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'agents')))
from text_to_speech import text_to_speech, save_audio

# from strands import agent_orchestrator
# 
 Simulación temporal del orquestador. Sustituir por import real cuando se integre strands.
def agent_orchestrator(query: str) -> str:
    return f"[SIMULACIÓN] Jarvis recibió la petición: '{query}'"

app = FastAPI()

# Permitir conexión desde tu frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Cambia si tu frontend está en otro sitio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir imágenes estáticas
app.mount("/pictures", StaticFiles(directory="..\\data\\pictures"), name="pictures")
app.mount("/segmentations", StaticFiles(directory="..\\data\\segmentations"), name="segmentations")

# MODELO PARA MENSAJES DE TEXTO
class ChatInput(BaseModel):
    message: str

class TextToSpeechInput(BaseModel):
    text: str

# ENDPOINT DE INTERACCIÓN DE TEXTO
@app.post("/interact")
async def interact(input: ChatInput):
    try:
        response = str(agent_orchestrator(input.message))
        return {"response": response}
    except Exception as e:
        return {"error": f"Fallo al invocar el orquestador: {str(e)}"}

# ENDPOINT PARA SUBIR IMÁGENES Y LANZAR CLASIFICACIÓN
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        os.makedirs("pictures", exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = file.filename.split('.')[0].lower()
        ext = file.filename.split('.')[-1]
        filename = f"{base_name}_{timestamp}.{ext}"
        filepath = os.path.join("pictures", filename)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        patient_identifier = base_name.replace("_", " ").title()
        prompt = f"Clasifica las imágenes de {patient_identifier}"

        response = str(agent_orchestrator(prompt))
        return {"response": response}

    except Exception as e:
        return {"error": f"Error al procesar imagen: {str(e)}"}

# ENDPOINT PARA TEXT-TO-SPEECH
@app.post("/text-to-speech")
async def tts(input: TextToSpeechInput):
    try:
        audio = text_to_speech(input.text)
        return StreamingResponse(audio, media_type="audio/mpeg")
    except Exception as e:
        return {"error": f"Error en la conversión de texto a voz: {str(e)}"}
