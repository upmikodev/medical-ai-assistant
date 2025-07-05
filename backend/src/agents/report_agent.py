from strands import Agent
from strands.tools import tool
import json
import os
from src.config.config import strands_model_mini
from src.config.prompts import report_system_prompt
from src.tools.file_system_tools import write_file_to_local
from src.tools.file_system_tools import read_file_from_local
from src.tools.report_pdf_agent import generate_pdf_from_report
@tool()

def report_agent(
    patient_identifier: str,
    classification: str,
    segmentation: str,
    knowledge: str,
    triage: str
) -> str:
    """
    Genera un reporte médico para un paciente en base al nombre del paciente,
    información recuperada a través de RAG de la base de conocimiento,
    la clasificación y segmentación de las imágenes MRI y el triaje automático.

    Args:
        - patient_identifier (str): El nombre del paciente en formato Nombre_Apellido1_Apellido2 o Nombre_Apellido1.
        - classification (str): Resultado de la clasificación de las imágenes MRI.
        - segmentation (str): Resultado de la segmentación de las imágenes MRI.
        - knowledge (str): Información recuperada a través de RAG de la base de conocimiento.
        - triage (str): Resultado del triaje automático.
    
    Tools:
        - write_file_to_local(path: str, content: str): Guarda el reporte en un archivo local.
    
    Returns:
        - report_path (str): Ruta del archivo final que recibirá el usuario.
    """
    try:
        report_agent = Agent(
            model=strands_model_mini,
            tools=[
                read_file_from_local,
                write_file_to_local,
                generate_pdf_from_report
            ],
            system_prompt=report_system_prompt
        )
        return report_agent(patient_identifier)
    except Exception as e:
        return json.dumps({
            "patient_identifier": patient_identifier,
            "classification": classification,
            "segmentation": segmentation,
            "knowledge": knowledge,
            "triage": triage,
            "error": str(e)
        })