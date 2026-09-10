from ..LLMInterface import LLMFactoryInterface
from cohere import Client
from ..LLMEnums import CohereEnums


class CohereProvider(LLMFactoryInterface):
    def __init__(
        self,
        api_key: str,
        input_max_chars: int = 16000,
        max_tokens: int = 1000,
        temperature: float = 0.1,
    ):
        self.api_key = api_key
        self.input_max_chars = input_max_chars
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system_prompt = None

        self.gen_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = Client(api_key=self.api_key)

    def set_model(self, model_id: str):
        self.gen_model_id = model_id

    def set_embedding_model(self, embedding_id: str, size: int):
        self.embedding_model_id = embedding_id or CohereEnums.EMBEDDING_V3.value
        self.embedding_size = size

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
            raise ValueError("Cohere client is not initialized")

        if not self.gen_model_id:
            raise ValueError("Generation Model is not initialized")

        max_output_token = max_output_token or self.max_tokens
        temperature = temperature or self.temperature

        messages = chat_history.copy()
        messages.append({"role": "user", "content": self._process_text(prompt)})

        response = self.client.chat(
            model=self.gen_model_id,
            message=messages[-1]["content"] if messages else prompt,
            chat_history=messages[:-1] if len(messages) > 1 else [],
            temperature=temperature,
            max_tokens=max_output_token,
            preamble=system_prompt,
        )

        if not response or not response.text:
            raise ValueError("Error generating text from Cohere model")

        return response.text

    def embed_text(self, text: str, embedding_type: str = None):
        if not self.client:
            raise ValueError("Cohere client is not initialized")

        model = self.embedding_model_id or CohereEnums.EMBEDDING_V3.value

        input_type = "search_query" if embedding_type == "query" else "search_document"

        response = self.client.embed(
            texts=[self._process_text(text)], model=model, input_type=input_type
        )

        if not response or len(response.embeddings) == 0:
            raise ValueError("Error while embedding from Cohere model")

        return response.embeddings[0]

    def embed_texts(self, texts: list, embedding_type: str = None):
        if not self.client:
            raise ValueError("Cohere client is not initialized")

        model = self.embedding_model_id or CohereEnums.EMBEDDING_V3.value

        input_type = "search_query" if embedding_type == "query" else "search_document"

        processed_texts = [self._process_text(t) for t in texts]

        response = self.client.embed(
            texts=processed_texts, model=model, input_type=input_type
        )

        if not response or len(response.embeddings) == 0:
            raise ValueError("Error while embedding from Cohere model")

        return response.embeddings

    def build_prompt(self, prompt: str, role: str):
        return {"role": role, "content": self._process_text(prompt)}
