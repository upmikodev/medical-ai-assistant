import os
import json
import logging
import asyncio
from datetime import datetime

# Import the main orchestrator agent
from orchestrator import agent_orchestrator

# Import config to ensure models are loaded and asyncio policy is set (if on Windows)
from config import configure_asyncio_policy, strands_model_planner_orchestrator # Check if orchestrator model loaded

# Configure logging for the main application
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


def create_required_directories():
    """Creates directories required for the application if they don't exist."""
    dirs_to_create = ["pictures", "models", "outputs"] # Added outputs for generated files
    for directory in dirs_to_create:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                logger.info(f"Created directory: ./{directory}")
            except OSError as e:
                logger.error(f"Error creating directory ./{directory}: {e}")
                # Depending on the error, you might want to exit or handle it differently

    # Check for the classifier model and provide a warning if it's missing or a dummy.
    classifier_model_path = "models/brain_tumor_classifier.pkl"
    if not os.path.exists(classifier_model_path):
        logger.warning(f"Classifier model '{classifier_model_path}' not found.")
        logger.warning("The AGENTE CLASIFICACIÓN will not function correctly without it.")
        # Optionally, create a dummy file to prevent crashes in some parts of the tool,
        # but it won't make the classifier work.
        # with open(classifier_model_path, "w") as f:
        #     f.write("dummy model content")
        # logger.info(f"Created a dummy '{classifier_model_path}'. Replace with the actual model.")
    else:
        # Basic check if it's a dummy file (e.g., by size or content if you have a known dummy signature)
        # This is a simple size check, might need to be more robust
        if os.path.getsize(classifier_model_path) < 1024: # Assuming a real model is larger than 1KB
             logger.warning(f"The classifier model at '{classifier_model_path}' seems very small. Ensure it is the correct, trained model.")


def run_swarm(user_query: str):
    """Runs the multi-agent swarm with the given user query."""
    logger.info(f"--- Starting Multi-Agent Swarm ---SERVICE REQUEST---User Query: {user_query}")

    if not agent_orchestrator or not strands_model_planner_orchestrator:
        logger.error("Orchestrator agent or its model is not initialized. Cannot proceed.")
        print("CRITICAL ERROR: Orchestrator agent or its model failed to initialize. Check logs.")
        return

    try:
        # The orchestrator agent is expected to handle the entire workflow based on its prompt
        # It will call the planner, then execute the plan using its tools (which call other agents)
        final_response = agent_orchestrator(user_query)
        
        logger.info("--- Orchestrator Final Response ---")
        # The response might be a JSON string from one of the tools, 
        # a direct text response, or content of a file.
        # The Orchestrator's prompt guides it to return the content of the final validated file.
        try:
            # If the orchestrator managed to read a file and pass its content as JSON
            parsed_json = json.loads(final_response)
            if "content" in parsed_json:
                logger.info("Final result (file content from JSON):")
                print("\n=== Final Report/Output ===")
                print(parsed_json["content"])
            elif "error" in parsed_json:
                logger.error(f"Orchestrator reported an error: {parsed_json['error']}")
                print(f"\n=== Error from Swarm ===\n{parsed_json['error']}")
            else:
                logger.info("Final result (JSON):")
                print("\n=== Final Result (JSON) ===")
                print(json.dumps(parsed_json, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            # If not JSON, print as plain text - this could be the direct content of a file or a message.
            logger.info("Final result (plain text):")
            print("\n=== Final Report/Output ===")
            print(final_response)
            
    except Exception as e:
        logger.error(f"An unexpected error occurred during swarm execution: {e}", exc_info=True)
        print(f"\n=== Swarm Execution Failed ===\nAn unexpected error occurred: {e}")
    finally:
        logger.info("--- End of Multi-Agent Swarm Execution ---")

if __name__ == "__main__":
    # Configure asyncio policy for Windows if necessary (important for Strands/LiteLLM)
    configure_asyncio_policy()

    # Create necessary directories and check for critical files
    create_required_directories()

    # --- Example User Queries ---
    # Ensure that 'execute_brain_tumor_classifier.py' and the required model/image paths are set up correctly.
    
    # Query 1: Full workflow request for a specific patient ID
    user_input_1 = "El identificador del paciente a analizar es carlos_perez_paco. Necesito una clasificación del tumor, luego una segmentación de la imagen clasificada, después un informe RAG sobre el tipo de tumor, y finalmente un reporte completo validado que incluya todos los resultados y un gráfico."
    
    # Query 2: Classification for a specific image path (ensure 'pictures/sample_tumor_image.png' exists)
    # Create a dummy image for testing if it doesn't exist
    # if not os.path.exists("pictures/sample_tumor_image.png"):
    #     try:
    #         with open("pictures/sample_tumor_image.png", "w") as f: f.write("dummy png content")
    #         logger.info("Created dummy 'pictures/sample_tumor_image.png' for testing Query 2.")
    #     except IOError as e:
    #         logger.error(f"Could not create dummy image: {e}")
    # user_input_2 = "Analiza la imagen en 'pictures/sample_tumor_image.png' para detectar tumores y genera un reporte simple."

    # Query 3: Test case for file not found by classifier
    # user_input_3 = "Clasifica la imagen para el paciente 'paciente_inexistente_123' y dame el resultado."

    # --- Select a query to run ---
    selected_user_query = user_input_1
    # selected_user_query = user_input_2
    # selected_user_query = user_input_3

    # Before running, ensure a .env file with OPENAI_API_KEY is present in the same directory.
    print(f"\nRunning swarm with query: \"{selected_user_query}\"\n")
    run_swarm(selected_user_query)

    # --- To run from command line, you can save this and execute: python main.py --- 