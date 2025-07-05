from strands import Agent
from strands.tools import tool
import json
import logging

from src.config.config import strands_model_mini
from src.config.prompts import planner_system_prompt

# logger ya configurado en main, pero lo importamos aquí
logger = logging.getLogger(__name__)

@tool()
def planner_agent(query: str) -> str:
    """
    Invoca al Planner agent para obtener un plan a partir de la petición del usuario.

    Args:
        query (str): La petición o descripción de tarea del usuario.

    Returns:
        str: Plan generado por el Planner agent como cadena.
    """
    try:
        agent_planner = Agent(
            model=strands_model_mini,
            tools=[],  # no tools para el planner puro
            system_prompt=planner_system_prompt
        )

        result = str(agent_planner(query))

        # registrar resumen humano-legible
        logger.info(f"📝 Plan propuesto por Planner: {result}")

        return result

    except Exception as e:
        logger.error(f"❌ Error en planner_agent: {e}")
        return json.dumps({"error": str(e)})
