# ---------------------------------------------------------------------------
# LLM Factory — returns a LangChain chat model based on the user's choice.
# Currently supports: Mistral AI (default) and Groq.
# ---------------------------------------------------------------------------

import logging

# LangChain wrappers around each provider's API
from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq

# Base type that all LangChain chat models implement
from langchain_core.language_models import BaseChatModel

from totem.config import MISTRAL_API_KEY, GROQ_API_KEY, SUPPORTED_MODELS

logger = logging.getLogger(__name__)


def get_llm(model_choice: str = "mistral") -> BaseChatModel:
    """
    Return a LangChain chat model for the given provider name.

    Args:
        model_choice: One of the keys in SUPPORTED_MODELS ("mistral" | "groq").

    Returns:
        A LangChain BaseChatModel instance ready to call .invoke().

    Raises:
        ValueError if the required API key is missing from the environment.
    """
    # Look up the model config; fall back to 'mistral' if unknown.
    info = SUPPORTED_MODELS.get(model_choice)
    if not info:
        logger.warning(f"Unknown model '{model_choice}', falling back to mistral")
        info = SUPPORTED_MODELS["mistral"]

    provider = info["provider"]
    model_name = info["default_model"]

    # Instantiate the correct LangChain wrapper based on provider
    if provider == "groq":
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not set. Add it to your .env file or export it."
            )
        return ChatGroq(api_key=GROQ_API_KEY, model=model_name, temperature=0.3)

    # Default: Mistral AI
    if not MISTRAL_API_KEY:
        raise ValueError(
            "MISTRAL_API_KEY not set. Add it to your .env file or export it."
        )
    return ChatMistralAI(
        api_key=MISTRAL_API_KEY, model=model_name, temperature=0.3
    )
