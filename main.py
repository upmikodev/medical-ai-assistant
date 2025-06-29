from src.agents.orchestrator_agent import agent_orchestrator

if __name__ == "__main__":
    query = "Dame la informacion, clasifica y segmentalas imagens de Lucía Rodríguez, si la probabilidad de que tenga un tumor es mas del 50% "
    response = str(agent_orchestrator(query))

    print(response)
