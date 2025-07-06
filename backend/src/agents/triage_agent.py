import re
import json
import logging
from strands import Agent
from strands.tools import tool
from src.config.config import strands_model_4_1
from src.config.prompts import triage_assistant_system_prompt
from src.tools.file_system_tools import write_file_to_local

# logger ya configurado en main
logger = logging.getLogger(__name__)

@tool()
def triage_agent(query: str) -> str:
    """
    Evaluates the clinical case of a patient and estimates the urgency level.

    Args:
        query (str): The clinical case data provided by other agents, structured as a JSON string.

    Tools:
    - write_file_to_local

    Returns:
        str: A JSON string with the urgency level and justification for triage.
    """
    try:
        triage = Agent(
            model=strands_model_4_1,
            tools=[
                write_file_to_local,
            ],
            system_prompt=triage_assistant_system_prompt
        )
        result = triage(query)

        # resumen human-readable
        logger.info(f"🚨 Triage result: {result}")

        return result
    except Exception as e:
        logger.error(f"❌ Error en triage_agent: {e}")
        return json.dumps({
            "error": str(e)
        })

