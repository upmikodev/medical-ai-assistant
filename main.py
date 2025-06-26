from src.agents.orchestrator_agent import orchestrator_agent

if __name__ == "__main__":
    query = "Clasifificame las imágenes de Carlos Pérez Paco y si la probabilidad es de mas de 60% que tenga tumor gegmentala "
    response = orchestrator_agent(query)

    print(response)
