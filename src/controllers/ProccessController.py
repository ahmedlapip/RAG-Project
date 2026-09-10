from .BaseController import BaseController
from .ProjectController import ProjectController
import re
from src.models.enums import FileExtEnums
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..models.repos.data_chunk_repo import DataChunkRepository
from fastapi import Request
from ..models.db_schemes import DataChunk
from bson import ObjectId
from langchain_core.documents.base import Document


class ProcessController(BaseController):
    def __init__(self, proj_id):
        super().__init__()
        self.proj_id = proj_id
        self.path_dir = ProjectController().get_proj_dir(proj_id=proj_id)

    def get_ext(self, file_path: str):
        return re.split(r"[^a-zA-Z0-9]+", file_path)[-1]

    def loader(self, file_path: str):
        file_ext = self.get_ext(file_path=file_path)
        if file_ext == FileExtEnums.ProccessExt.PDF.value:
            return PyMuPDFLoader(file_path)
        if file_ext == FileExtEnums.ProccessExt.TXT.value:
            return TextLoader(file_path, encoding="utf-8")
        return None

    def get_file_content(self, file_path):
        try:
            loader = self.loader(file_path=file_path)
            if loader:
                return loader.load()
            return None
        except Exception as e:
            print(f"Error loading file: {e}")
            return None

    async def insert_chunks(self, request: Request, body: list[DataChunk]):
        data_chunk_repo = DataChunkRepository(request.app.db_client)
        return await data_chunk_repo.create_many(body)

    def process_file_content(self, chunk_size: int, overlap: int, file_content: list):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            is_separator_regex=False,
        )
        file_contents = [rec.page_content for rec in file_content]
        file_metas = [rec.metadata for rec in file_content]
        chunks = text_splitter.create_documents(file_contents, metadatas=file_metas)

        return chunks

    def prepare_chunks_for_db(self, chunks: list, project_id: str) -> list[DataChunk]:


        data_chunks = []
        for idx, chunk in enumerate(chunks):
            if isinstance(chunk, Document):
                data_chunk = DataChunk(
                    chunk_text=chunk.page_content,
                    chunk_metadata=chunk.metadata,
                    chunk_order=idx + 1,
                    chunk_project_id=ObjectId(project_id),
                )
                data_chunks.append(data_chunk)
            else:
                data_chunk = DataChunk(
                    chunk_text=chunk.get("page_content", ""),
                    chunk_metadata=chunk.get("metadata", {}),
                    chunk_order=idx + 1,
                    chunk_project_id=ObjectId(project_id),
                )
                data_chunks.append(data_chunk)
        return data_chunks
