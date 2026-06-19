import os
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CRAWL4AI_URL = os.getenv("CRAWL4AI_URL", "http://localhost:11235")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

SUPPORTED_MODELS = {
    "mistral": {
        "display": "Mistral AI",
        "provider": "mistral",
        "default_model": "mistral-large-latest",
        "env_key": "MISTRAL_API_KEY",
    },
    "groq": {
        "display": "Groq (Mixtral)",
        "provider": "groq",
        "default_model": "mixtral-8x7b-32768",
        "env_key": "GROQ_API_KEY",
    },
}
