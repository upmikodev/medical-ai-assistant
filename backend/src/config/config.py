import os
from dotenv import load_dotenv
from strands.models.openai import OpenAIModel
import nest_asyncio
import base64

nest_asyncio.apply()

# Load environment variables from .env file
load_dotenv()
print("Attempting to load .env file...")

# API Keys - OpenAIModel will look for OPENAI_API_KEY in environment variables
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"OPENAI_API_KEY found in environment. Length: {len(api_key)}, Ends with: ...{api_key[-4:] if len(api_key) > 4 else '****'}")
else:
    print("CRITICAL: OPENAI_API_KEY not found in environment variables. Please ensure it is set in your .env file or system environment.")

# Langfuse environment variables
os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY")
os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY")
os.environ["LANGFUSE_HOST"] = os.getenv("LANGFUSE_HOST")

otel_endpoint = str(os.environ.get("LANGFUSE_HOST")) + "/api/public/otel/v1/traces"
# Create authentication token for OpenTelemetry
auth_token = base64.b64encode(f"{os.environ.get('LANGFUSE_PUBLIC_KEY')}:{os.environ.get('LANGFUSE_SECRET_KEY')}".encode()).decode()
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = otel_endpoint
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {auth_token}"

# Model Definitions
print("Initializing Strands OpenAIModels...")
try:
    strands_model_nano = OpenAIModel(
        client_args={"api_key": os.getenv("OPENAI_API_KEY")},
        model_id="gpt-4.1-nano"
    )
    strands_model_mini = OpenAIModel(
        client_args={"api_key": os.getenv("OPENAI_API_KEY")},
        model_id="gpt-4.1-mini"
    )
    print("Strands OpenAIModels initialized successfully.")

except Exception as e:
    print(f"CRITICAL ERROR during OpenAIModel initialization: {e}")
    print("This usually means an issue with your OPENAI_API_KEY (not found, invalid, expired, insufficient quota/permissions for the specified models) or the model names.")
    print("Please double-check your .env file for OPENAI_API_KEY and ensure the models (gpt-4.1-nano, gpt-4.1-mini) are accessible with your key.")
    strands_model_nano = None
    strands_model_mini = None

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

    if strands_model_nano:
        print(f"Nano OpenAIModel model_id: {strands_model_nano.config['model_id']}")
    else:
        print("Nano OpenAIModel (strands_model_nano) is None.")

    if strands_model_mini:
        print(f"Mini OpenAIModel model_id: {strands_model_mini.config['model_id']}")
    else:
        print("Mini OpenAIModel (strands_model_mini) is None.")