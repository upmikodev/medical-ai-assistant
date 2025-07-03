from strands import Agent
from strands.tools import tool
import json
from src.config.config import strands_model_mini
from src.config.prompts import clasificacion_system_prompt
from src.tools.execute_brain_tumor_classifier import classify_tumor_from_image
from src.tools.file_system_tools import read_file_from_local, write_file_to_local


@tool()
def clasificacion_agent(input_file: str = "data/temp/lister.json") -> str:
    """
    El LLM leerá `data/temp/lister.json`, recorrerá la lista `scans`
    y llamará a `classify_tumor_from_pair` para cada par FLAIR+T1CE.
    No necesita argumentos de entrada.
    
    Args:
        dummy (str): Dummy argument to match the tool signature.

    Tools:
        - classify_tumor_from_image
        - read_file_from_local
        - write_file_to_local

    """
    try:
        # Extract last names to build path
        classifier_agent = Agent(
            model=strands_model_mini,
            tools=[
            classify_tumor_from_image,
            read_file_from_local,
            write_file_to_local,
            ],
            system_prompt=clasificacion_system_prompt
        )
        return classifier_agent("")
    except Exception as e:
        return json.dumps({"error": str(e)})