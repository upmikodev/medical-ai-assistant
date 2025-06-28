from src.agents.orchestrator_agent import orchestrator_agent

if __name__ == "__main__":
    query = "Lucía Rodríguez"
    response = orchestrator_agent(query)

    print(response)
