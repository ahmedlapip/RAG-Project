from enum import Enum

class LLMEnums(Enum):
    OPENAI = "OpenAI"
    COHERE = "CoHere"


class OpenAIEnums(Enum):
    SYSTEM = "System"
    USER = "User"
    ASSISTANT = "Assistant"

class CoHereEnums(Enum):
    SYSTEM = "System"
    USER = "User"
    ASSISTANT = "Assistant"

    DOCUMENT = "Search_Document"
    QUERY = "Search_Query"

class DocumentTypeEnum(Enum):
    DOCUMENT = "Document"
    QUERY = "Query"