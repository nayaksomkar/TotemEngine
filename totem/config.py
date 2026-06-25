# ---------------------------------------------------------------------------
# Configuration — loads environment variables and defines supported AI models.
# ---------------------------------------------------------------------------

import os
from dotenv import load_dotenv

# Load .env file from the project root into environment variables
load_dotenv()

# --- Environment variables with defaults ---
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Supported LLM models ---
SUPPORTED_MODELS = {
    "mistral": {
        "display": "Mistral AI",
        "provider": "mistral",
        "default_model": "mistral-large-latest",
        "env_key": "MISTRAL_API_KEY",
    },
    "groq": {
        "display": "Groq (Llama 3.3 70B)",
        "provider": "groq",
        "default_model": "llama-3.3-70b-versatile",
        "env_key": "GROQ_API_KEY",
    },
}
