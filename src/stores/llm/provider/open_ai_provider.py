from ..LLMInterface import LLMFactoryInterface
from openai import OpenAI
from ..LLMEnums import OpenAIEnums


class OpenAIProvider(LLMFactoryInterface):
    def __init__(
        self,
        api_key: str,
        api_url: str = None,
        input_max_chars: int = 1000,
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ):

        self.api_key = api_key
        self.api_url = api_url
        self.input_max_chars = input_max_chars
        self.max_tokens = max_tokens
        self.temperature = temperature

        self.gen_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key=self.api_key, base_url=self.api_url if api_url else None
        )

    def set_model(self, model_id: str):
        self.gen_model_id = model_id

    def set_embedding_model(self, embedding_id: str, size: int):
        self.embedding_model_id = embedding_id
        self.embedding_size = size

    def _process_text(self, text: str):
        return text[: self.input_max_chars].strip()

    def generate_text(
        self,
        prompt: str,
        max_output_token: int = None,
        temperature: float = None,
        chat_history: list = None,
    ):
        if chat_history is None:
            chat_history = []

        if not self.client:
            raise ValueError("OpenAI client is not initialized")

        if not self.gen_model_id:
            raise ValueError("Generation Model is not initialized")

        max_output_token = max_output_token or self.max_tokens
        temperature = temperature or self.temperature

        chat_history.append(self.build_prompt(prompt, OpenAIEnums.USER.value))

        response = self.client.chat.completions.create(
            model=self.gen_model_id,
            messages=chat_history,
            max_tokens=max_output_token,
            temperature=temperature,
        )

        if not response or len(response.choices) == 0:
            raise ValueError("Error generating text from OpenAI model")

        return response.choices[0].message.content

    def embed_text(self, text: str, embedding_type: str = None):
        if not self.client:
            raise ValueError("OpenAI client is not initialized")

        if not self.embedding_model_id:
            raise ValueError("Embedding model ID is missing")

        response = self.client.embeddings.create(
            input=text, model=self.embedding_model_id
        )

        if not response or len(response.data) == 0:
            raise ValueError("Error while embedding from OpenAI model")

        return response.data[0].embedding

    def build_prompt(self, prompt: str, role: str):
        return {"role": role, "content": self._process_text(prompt)}
