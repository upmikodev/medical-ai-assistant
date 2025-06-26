from strands import Agent
from strands.tools import tool
import json
from src.config.config import strands_model_mini
from src.config.prompts import triage_assistant_system_prompt

@tool()
def triage_agent(query: str) -> str:
    """
    Evaluates the clinical case of a patient and estimates the urgency level.

    Args:
        query (str): The clinical case data provided by other agents, structured as a JSON string.

    Returns:
        str: A JSON string with the urgency level and justification for triage.
    """

    try:
        triage_agent = Agent(
            model=strands_model_mini,
            tools=[
            ],
            system_prompt=triage_assistant_system_prompt
        )
        return triage_agent(query)
    except Exception as e:
        return json.dumps({
            "error": str(e)
        })