from strands import Agent
from strands.tools import tool
import json
import logging

from src.config.config import strands_model_mini
from src.config.prompts import rag_system_prompt
from src.tools.rag_tool import rag_tool
from src.tools.file_system_tools import write_file_to_local

# logger ya configurado en main
logger = logging.getLogger(__name__)

@tool()
def rag_agent(query: str) -> str:
    """
    Agente que utiliza el modelo RAG para recuperar información relevante de un paciente
    a partir de una consulta en lenguaje natural. Utiliza la herramienta `rag_tool` para buscar
    información en la base de datos vectorial asociada al paciente.

    Args:
        query (str): Consulta en lenguaje natural sobre el caso clínico del paciente.

    Returns:
        str: Texto recuperado con información relevante del paciente o mensaje de error si ocurre algún problema.
    """
    try:
        rag_agent = Agent(
            model=strands_model_mini,
            tools=[
                rag_tool,
                write_file_to_local
            ],
            system_prompt=rag_system_prompt
        )

        result = rag_agent(query)

        # registrar resumen humano-legible
        logger.info(f"🔎 RAG respuesta: {result}")

        return result

    except Exception as e:
        logger.error(f"❌ Error en rag_agent: {e}")
        return json.dumps({"error": str(e)})
