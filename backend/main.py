from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import sys

# cargar variables de entorno
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

# ================
# LOGGER
# ================
os.makedirs("backend/data/logs", exist_ok=True)
log_file_path = "backend/data/logs/progreso.txt"

# limpia el log al arrancar
open(log_file_path, "w", encoding="utf-8").close()

# logger tradicional
file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

# redirigir también stdout a progreso.txt
sys.stdout = open(log_file_path, "a", encoding="utf-8")

# ================
# FASTAPI
# ================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # recuerda limitar en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.agents.orchestrator_agent import agent_orchestrator

# ================
# ENDPOINTS
# ================

class QueryInput(BaseModel):
    query: str

@app.post("/query")
def process_query(input: QueryInput):
    try:
        response = agent_orchestrator(input.query)
        return {"response": str(response)}
    except Exception as e:
        logger.error(f"Fallo orquestador: {e}")
        return {"error": str(e)}

@app.get("/progress", response_class=PlainTextResponse)
async def get_progress():
    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "Sin progreso todavía."
    except Exception as e:
        logger.error(f"Error leyendo progreso: {e}")
        return f"Error leyendo progreso: {str(e)}"

@app.get("/download/{filename}")
async def download_report(filename: str):
    file_path = os.path.join("backend", "data", "reportes", filename)
    if not os.path.exists(file_path):
        return {"error": "Archivo no encontrado"}
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )
