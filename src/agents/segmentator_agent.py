from strands import Agent
from strands.tools import tool
import json
from src.config.config import strands_model_mini
from src.config.prompts import segmentator_system_prompt
from src.tools.execute_brain_tumor_segmentation import segmenter_tumor_from_image
from src.tools.file_system_tools import read_file_from_local, write_file_to_local

@tool
def segmentator_agent(input_file: str = "data/temp/lister.json" 
) -> str:
    """
    El LLM leerá `data/temp/lister.json`, recorrerá la lista `scans`.
    y llamará a `segmenter_tumor_from_image` para cada par FLAIR+T1CE.
    argumentos de entrada data/temp/lister.json
    """
    try:
        # Extract last names to build path
        segmentator_agent = Agent(
            model=strands_model_mini,
            tools=[
            segmenter_tumor_from_image,
            read_file_from_local,
            write_file_to_local,
            ],
            system_prompt=segmentator_system_prompt
        )
        return segmentator_agent(input_file)
    except Exception as e:
        return json.dumps({"error": str(e)})