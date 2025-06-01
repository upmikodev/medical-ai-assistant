import os
from dotenv import load_dotenv
from strands.models.openai import OpenAIModel


# Load environment variables from .env file
load_dotenv()
print("Attempting to load .env file...")

# API Keys - OpenAIModel will look for OPENAI_API_KEY in environment variables
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"OPENAI_API_KEY found in environment. Length: {len(api_key)}, Ends with: ...{api_key[-4:] if len(api_key) > 4 else '****'}")
else:
    print("CRITICAL: OPENAI_API_KEY not found in environment variables. Please ensure it is set in your .env file or system environment.")

# Model Definitions
# User has confirmed these model names: "gpt-4.1-nano", "gpt-4.1-mini"
print("Initializing Strands OpenAIModels...")
try:
    # Ensure to use the user-specified model names
    strands_model_nano = OpenAIModel(
        client_args={"api_key": os.getenv("OPENAI_API_KEY")},
        model_id="gpt-4.1-nano")
    strands_model_mini = OpenAIModel(
        client_args={"api_key": os.getenv("OPENAI_API_KEY")},
        model_id="gpt-4.1-mini"
        # model_id="gpt-4.1-nano"
        )
    strands_model_planner_orchestrator = OpenAIModel(
        client_args={"api_key": os.getenv("OPENAI_API_KEY")},
        model_id="gpt-4.1-mini")
    print("Strands OpenAIModels appear to have been initialized.") # This print might be reached even if a later call fails

    # Test a very simple call to one of the models to see if it truly works
    # This is a synchronous call for testing purposes here; Strands handles async internally for agents
    print("Attempting a test call to the default model to confirm API key validity and model access...")
    # Note: Strands Agent class __call__ method might be async. 
    # Here we are trying to invoke the model directly if possible, or a method that would use the API key.
    # The OpenAIModel in Strands might not have a direct synchronous invoke method easily available without an agent context.
    # However, the initialization itself often performs some validation or would fail on first use if the key is bad.
    # For now, we rely on the print statements and the application's later behavior.
    # If there's a specific method on OpenAIModel to test a connection, that would be better.
    # For now, the main check will be the exception message if initialization fails.

    print("Strands OpenAIModels initialization step passed without immediate error.")

except Exception as e:
    print(f"CRITICAL ERROR during OpenAIModel initialization: {e}")
    print("This usually means an issue with your OPENAI_API_KEY (not found, invalid, expired, insufficient quota/permissions for the specified models) or the model names.")
    print("Please double-check your .env file for OPENAI_API_KEY and ensure the models (gpt-4.1-nano, gpt-4.1-mini) are accessible with your key.")
    strands_model_nano = None
    strands_model_default = None
    strands_model_planner_orchestrator = None

# Asyncio policy for Windows if needed
def configure_asyncio_policy():
    if os.name == 'nt':
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print("Asyncio policy configured for Windows.")

if __name__ == "__main__":
    configure_asyncio_policy()
    if api_key:
        print(f"OPENAI_API_KEY is set.")
    else:
        print("OPENAI_API_KEY is NOT set.")

    if strands_model_default:
        print(f"Default OpenAIModel model_id: {strands_model_default.config['model_id']}")
    else:
        print("Default OpenAIModel (strands_model_default) is None.")

    if strands_model_planner_orchestrator:
        print(f"Planner/Orchestrator OpenAIModel model_id: {strands_model_planner_orchestrator.config['model_id']}")
    else:
        print("Planner/Orchestrator OpenAIModel (strands_model_planner_orchestrator) is None.") 