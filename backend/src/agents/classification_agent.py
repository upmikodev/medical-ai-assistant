from strands import Agent
from strands.tools import tool
import json
import logging

from src.config.config import strands_model_mini
from src.config.prompts import clasificacion_system_prompt
from src.tools.execute_brain_tumor_classifier import classify_tumor_from_image
from src.tools.file_system_tools import read_file_from_local, write_file_to_local

# reutilizamos logger ya configurado en main
logger = logging.getLogger(__name__)

@tool()
def clasificacion_agent(input_file: str = "data/temp/lister.json") -> str:
    """
    Este agente recorre `data/temp/lister.json` con los pares FLAIR+T1CE
    y clasifica la probabilidad de tumor.

    Args:
        input_file (str): Ruta al archivo JSON de entrada con la lista de escaneos.
    
    Tools:
        - classify_tumor_from_image(flair_path: str, t1ce_path: str) -> str
        - read_file_from_local(path: str, encoding: str = "utf-8") -> str
        - write_file_to_local(path: str, content: str) -> str

    Returns:
        str: Resultado en JSON con la probabilidad de tumor
    """
    try:
        classifier_agent = Agent(
            model=strands_model_mini,
            tools=[
                classify_tumor_from_image,
                read_file_from_local,
                write_file_to_local,
            ],
            system_prompt=clasificacion_system_prompt
        )
        result = classifier_agent("")  # sin prompt extra porque el system_prompt ya instruye

        # registrar resultado humano-legible
        logger.info(f"🧪 Resumen de clasificación: {result}")

        return result

    except Exception as e:
        logger.error(f"❌ Error en clasificacion_agent: {e}")
        return json.dumps({"error": str(e)})

