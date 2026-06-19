import logging

from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq
from langchain_core.language_models import BaseChatModel

from totem.config import MISTRAL_API_KEY, GROQ_API_KEY, SUPPORTED_MODELS

logger = logging.getLogger(__name__)


def get_llm(model_choice: str = "mistral") -> BaseChatModel:
    info = SUPPORTED_MODELS.get(model_choice)
    if not info:
        logger.warning(f"Unknown model '{model_choice}', falling back to mistral")
        info = SUPPORTED_MODELS["mistral"]

    provider = info["provider"]
    model_name = info["default_model"]

    if provider == "groq":
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not set. Add it to your .env file or export it."
            )
        return ChatGroq(api_key=GROQ_API_KEY, model=model_name, temperature=0.3)

    if not MISTRAL_API_KEY:
        raise ValueError(
            "MISTRAL_API_KEY not set. Add it to your .env file or export it."
        )
    return ChatMistralAI(
        api_key=MISTRAL_API_KEY, model=model_name, temperature=0.3
    )
