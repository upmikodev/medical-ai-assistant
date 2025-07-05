from fastapi import FastAPI
from pydantic import BaseModel
from src.agents.orchestrator_agent import agent_orchestrator
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Si el frontend está en otro puerto/origen (por ejemplo localhost:3000), permite CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod puedes limitar esto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryInput(BaseModel):
    query: str

@app.post("/query")
def process_query(input: QueryInput):
    response = agent_orchestrator(input.query)
    return {"response": str(response)}
