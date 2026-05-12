# ABC is for designing interfase
from abc import ABC, abstractmethod


class LLMFactoryInterface(ABC):
    @abstractmethod
    def set_model(self, model_id: str):
        pass

    @abstractmethod
    def set_embedding_model(self, embedding_id: str, size: int):
        pass

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        max_output_token: int = None,
        temperature: float = None,
        chat_history: list = None,
    ):
        pass

    @abstractmethod
    def embed_text(self, text: str, embedding_type: str = None):
        pass

    @abstractmethod
    def build_prompt(self, prompt: str, role: str):
        pass
