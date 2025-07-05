from strands import Agent
from strands.tools import tool
import json
import os
import logging
import re

from src.config.config import strands_model_mini
from src.config.prompts import report_system_prompt
from src.tools.file_system_tools import write_file_to_local, read_file_from_local
from src.tools.report_pdf_agent import generate_pdf_from_report

# logger ya configurado en main
logger = logging.getLogger(__name__)

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
    
    Returns:
        JSON con resumen y ruta de descarga del PDF
    """
    try:
        agent = Agent(
            model=strands_model_mini,
            tools=[
                read_file_from_local,
                write_file_to_local,
                generate_pdf_from_report
            ],
            system_prompt=report_system_prompt
        )
        result = agent(patient_identifier)

        # intentar capturar el nombre real del PDF
        match = re.search(r"([\w\-]+\.pdf)", result)
        pdf_filename = match.group(1) if match else None

        logger.info(f"✅ Informe clínico generado y validado para {patient_identifier}. "
                    f"Disponible en el archivo: {pdf_filename}")

        return json.dumps({
            "summary": f"✅ Informe clínico generado y validado para {patient_identifier}.",
            "pdf_path": f"/download/{pdf_filename}" if pdf_filename else None
        })
    except Exception as e:
        logger.error(f"❌ Error en report_agent: {e}")
        return json.dumps({
            "patient_identifier": patient_identifier,
            "classification": classification,
            "segmentation": segmentation,
            "knowledge": knowledge,
            "triage": triage,
            "error": str(e)
        })
