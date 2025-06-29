from strands import Agent
from strands.tools import tool
import json
from src.config.config import strands_model_mini
from src.config.prompts import rag_system_prompt
from src.tools.rag_tool import rag_tool

@tool()
def rag_agent(query: str) -> str:
    """
    Agente que utiliza el modelo RAG para recuperar información relevante de un paciente
    a partir de una consulta en lenguaje natural. Utiliza la herramienta `rag_tool` para buscar
    información en la base de datos vectorial asociada al paciente.

    Args:
        query (str): Consulta en lenguaje natural sobre el caso clínico del paciente.

    Tools:
        rag_tool (str): Herramienta para realizar la búsqueda semántica en la base de datos vectorial.

    Returns:
        str: Texto recuperado con información relevante del paciente o mensaje de error si ocurre algún problema.
    """
    try:
        rag_agent = Agent(
            model=strands_model_mini,
            tools=[
                rag_tool
            ],
            system_prompt=rag_system_prompt
        )
        return str(rag_agent(query))
    except Exception as e:
        return json.dumps({
            "error": str(e)
        })