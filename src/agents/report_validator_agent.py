from strands import Agent
from strands.tools import tool
import json
from src.config.config import strands_model_mini
from src.config.prompts import report_validator_system_prompt
from src.tools.file_system_tools import write_file_to_local
from src.tools.file_system_tools import read_file_from_local
from src.tools.report_pdf_agent import generate_pdf_from_report
from src.tools.extract_text_from_pdf import extract_text_from_pdf

@tool()
def report_validator_agent(paths_json: str) -> str:
    """
    
    Valida data/temp/report.json frente a los JSON fuente.
    Si hace falta, genera data/temp/report_validated.json + PDF corregido.
    
    paths_json debe ser exactamente el diccionario que devuelve
    ReportWriter, por ejemplo:
    {
      "report_json_path": "data/temp/report.json",
      "report_pdf_path":  "reportes/lucia_2025-06-12.pdf"
    }

    Returns:
        str: Un mensaje de validación:
            - "VALIDACIÓN APROBADA: El informe es fiel a los datos proporcionados."
            - "VALIDACIÓN RECHAZADA: Se han detectado inconsistencias. Se ha generado una nueva versión corregida. Ruta del nuevo archivo: <ruta>"
    """
    try:
        report_validator_agent = Agent(
            model=strands_model_mini,
            tools=[
                read_file_from_local,
                write_file_to_local,
                generate_pdf_from_report,
                extract_text_from_pdf
            ],
            system_prompt=report_validator_system_prompt
        )
        return report_validator_agent(paths_json)
    except Exception as e:
        return json.dumps({
            "report_path": paths_json,
            "error": str(e)
        })