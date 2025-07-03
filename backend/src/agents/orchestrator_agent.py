import re
from strands import Agent
from strands.tools import tool
import uuid
import json
import re
from src.config.config import strands_model_mini
from src.config.prompts import orchestrator_system_prompt
from src.agents.planner_agent import planner_agent
from src.agents.image_lister_agent import image_lister_agent
from src.agents.classification_agent import clasificacion_agent
from src.agents.segmentator_agent import segmentator_agent
from src.agents.rag_agent import rag_agent
from src.agents.triage_agent import triage_agent
from src.agents.report_agent import report_agent
from src.agents.report_validator_agent import report_validator_agent
from src.tools.file_system_tools import read_file_from_local

import uuid

try:
    agent_orchestrator= Agent(
        model=strands_model_mini, 
        tools=[
            planner_agent,
            image_lister_agent,
            clasificacion_agent,
            segmentator_agent,
            rag_agent,
            triage_agent,
            report_agent,
            report_validator_agent,
        ],
        system_prompt=orchestrator_system_prompt,
        trace_attributes={
            "session.id": str(uuid.uuid4()),
            "user.id": "ananju",
            "langfuse.tags": [
                "TFM"
            ]
    }
    )

except Exception as e:
    print(f"Error initializing AgentOrchestrator: {e}")
    agent_orchestrator = None