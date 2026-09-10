from ..LLMInterface import LLMFactoryInterface
from ..LLMEnums import OllamaEnums


class OllamaProvider(LLMFactoryInterface):
    def __init__(
        self,
        api_url: str = "http://localhost:11434",
        generation_model: str = None,
        embedding_model: str = None,
        input_max_chars: int = 16000,
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ):
        self.api_url = api_url
        self.generation_model = generation_model or OllamaEnums.GENERATION_DEFAULT.value
        self.embedding_model = embedding_model or OllamaEnums.EMBEDDING_DEFAULT.value
        self.input_max_chars = input_max_chars
        self.max_tokens = max_tokens
        self.temperature = temperature

        try:
            from openai import OpenAI
            self.client = OpenAI(
                base_url=f"{self.api_url}/v1",
                api_key="ollama"
            )
        except Exception:
            self.client = None

    def set_model(self, model_id: str):
        self.generation_model = model_id

    def set_embedding_model(self, embedding_id: str, size: int):
        self.embedding_model = embedding_id

    def _process_text(self, text: str):
        return text[: self.input_max_chars].strip()

    def generate_text(
        self,
        prompt: str,
        max_output_token: int = None,
        temperature: float = None,
        chat_history: list = None,
        system_prompt: str = None,
    ):
        if chat_history is None:
            chat_history = []

        if not self.client:
            raise ValueError("Ollama client is not initialized")

        if not self.generation_model:
            raise ValueError("Generation Model is not initialized")

        max_output_token = max_output_token or self.max_tokens
        temperature = temperature or self.temperature

        if system_prompt:
            chat_history.append({"role": "system", "content": system_prompt})

        chat_history.append(self.build_prompt(prompt, "user"))

        response = self.client.chat.completions.create(
            model=self.generation_model,
            messages=chat_history,
            max_tokens=max_output_token,
            temperature=temperature,
        )

        if not response or len(response.choices) == 0:
            raise ValueError("Error generating text from Ollama model")

        return response.choices[0].message.content

    def embed_text(self, text: str, embedding_type: str = None):
        if not self.client:
            raise ValueError("Ollama client is not initialized")

        if not self.embedding_model:
            raise ValueError("Embedding model ID is missing")

        response = self.client.embeddings.create(
            input=text, model=self.embedding_model
        )

        if not response or len(response.data) == 0:
            raise ValueError("Error while embedding from Ollama model")

        return response.data[0].embedding

    def build_prompt(self, prompt: str, role: str):
        return {"role": role, "content": self._process_text(prompt)}