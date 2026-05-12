from src.helpers.config import get_settings
from .LLMEnums import LLMEnums
from .provider.open_ai_provider import OpenAIProvider
from .provider.cohere_provider import CohereProvider
from .provider.ollama_provider import OllamaProvider


class LLMProviderFactory:
    def __init__(self):
        self.settings = get_settings()

    def create(self, provider: str = None):
        provider = provider or self.settings.GENERATION_BACKEND

        if provider == LLMEnums.OPENAI.value or provider == "OpenAI":
            return OpenAIProvider(
                api_key=self.settings.OPENAI_API_KEY,
                api_url=self.settings.OPENAI_API_BASE
                if self.settings.OPENAI_API_BASE
                else None,
                input_max_chars=self.settings.MAX_CHARACTERS,
                max_tokens=self.settings.MAX_TOKENS,
                temperature=self.settings.TEMPERATURE,
            )

        if provider == LLMEnums.COHERE.value or provider == "Cohere":
            return CohereProvider(
                api_key=self.settings.COHERE_API_KEY,
                input_max_chars=self.settings.MAX_CHARACTERS,
                max_tokens=self.settings.MAX_TOKENS,
                temperature=self.settings.TEMPERATURE,
            )

        if provider == LLMEnums.OLLAMA.value or provider == "Ollama":
            return OllamaProvider(
                api_url=self.settings.OLLAMA_API_URL,
                generation_model=self.settings.OLLAMA_GENERATION_MODEL,
                embedding_model=self.settings.OLLAMA_EMBEDDING_MODEL,
                input_max_chars=self.settings.MAX_CHARACTERS,
                max_tokens=self.settings.MAX_TOKENS,
                temperature=self.settings.TEMPERATURE,
            )

        raise ValueError(f"Provider {provider} not supported")


def get_llm_provider():
    factory = LLMProviderFactory()
    return factory.create()
