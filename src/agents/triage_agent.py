import re
import json
from strands import Agent
from strands.tools import tool
from src.config.config import strands_model_mini
from src.config.prompts import triage_assistant_system_prompt
from src.tools.file_system_tools import write_file_to_local

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
        triage_agent = Agent(
            model=strands_model_mini,
            tools=[
                write_file_to_local,
            ],
            system_prompt=triage_assistant_system_prompt
        )
        return triage_agent(query)
    except Exception as e:
        return json.dumps({
            "error": str(e)
        })
