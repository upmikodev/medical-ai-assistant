from strands import Agent
from strands.tools import tool
import json
import logging

from src.config.config import strands_model_4_1
from src.config.prompts import segmentator_system_prompt
from src.tools.execute_brain_tumor_segmentation import segmenter_tumor_from_image
from src.tools.file_system_tools import read_file_from_local, write_file_to_local

# logger ya configurado en main
logger = logging.getLogger(__name__)

@tool
def segmentator_agent(input_file: str = "data/temp/lister.json") -> str:
    """
    El LLM leerá `data/temp/lister.json`, recorrerá la lista `scans`.
    y llamará a `segmenter_tumor_from_image` para cada par FLAIR+T1CE.
    argumentos de entrada data/temp/lister.json
    """
    try:
        seg_agent = Agent(
            model=strands_model_4_1,
            tools=[
                segmenter_tumor_from_image,
                read_file_from_local,
                write_file_to_local,
            ],
            system_prompt=segmentator_system_prompt
        )
        result = seg_agent(input_file)

        # resumen human-readable
        logger.info(f"🧩 Segmentación completada: {result}")

        return result
    except Exception as e:
        logger.error(f"❌ Error en segmentator_agent: {e}")
        return json.dumps({"error": str(e)})
