from strands import Agent
from strands.tools import tool
import json
import logging

from src.config.config import strands_model_4_1
from src.config.prompts import planner_system_prompt

# logger ya configurado en main, pero lo importamos aquí
logger = logging.getLogger(__name__)

@tool()
def planner_agent(query: str) -> str:
    """
    Este agente es el encargado de planificar las tareas a realizar.
    Toma una petición del usuario y devuelve un plan de tareas.

    Tools:
        - No tiene herramientas.

    Args:
        query (str): La petición o descripción de tarea del usuario.

    Returns:
        str: Plan generado por el Planner agent como cadena.
    """
    try:
        agent_planner = Agent(
            model=strands_model_4_1,
            tools=[], 
            system_prompt=planner_system_prompt
        )

        result = str(agent_planner(query))

        # registrar resumen humano-legible
        logger.info(f"📝 Plan propuesto por Planner: {result}")

        return result

    except Exception as e:
        logger.error(f"❌ Error en planner_agent: {e}")
        return json.dumps({"error": str(e)})
