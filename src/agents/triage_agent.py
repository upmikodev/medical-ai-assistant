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
    Evalúa el caso clínico y estima el nivel de urgencia.
    """
    try:
        triage_agent = Agent(
            model=strands_model_mini,
            tools=[write_file_to_local],
            system_prompt=triage_assistant_system_prompt
        )

        result = triage_agent(query)
        result_str = str(result)

        # Extraer solo el primer JSON con campo "riesgo"
        json_blocks = re.findall(r'\{.*?\}', result_str, re.DOTALL)
        target_json = None

        for block in json_blocks:
            try:
                parsed = json.loads(block)
                if "riesgo" in parsed and (
                    "justificación_triaje" in parsed or "justificacion_triaje" in parsed
                ):
                    target_json = parsed
                    break
            except json.JSONDecodeError:
                continue

        if not target_json:
            raise ValueError("No se encontró JSON con campos esperados.")

        return json.dumps(target_json, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "error": f"Triage failed: {str(e)}"
        })
