from enum import Enum


class LLMEnums(Enum):
    OPENAI = "OpenAI"
    COHERE = "Cohere"
    OLLAMA = "Ollama"


class OpenAIEnums(Enum):
    SYSTEM = "System"
    USER = "User"
    ASSISTANT = "Assistant"


class CohereEnums(Enum):
    EMBEDDING_V3 = "embed-multilingual-v3.0"
    EMBEDDING_V3_LIGHT = "embed-multilingual-v3.0"
    COMMAND_R = "command-r"
    COMMAND_R_PLUS = "command-r-plus"


class OllamaEnums(Enum):
    GENERATION_DEFAULT = "qwen2.5:3b"
    EMBEDDING_DEFAULT = "nomic-embed-text"
