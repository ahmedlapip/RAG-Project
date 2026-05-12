from typing import Optional
from .BaseController import BaseController
from ..models.repos.data_chunk_repo import DataChunkRepository
from ..models.repos.project_repo import ProjectRepository
from ..stores.vectordb.provider.QdrantDB_provider import QDrantProvider
from ..stores.llm.LLMProvideFactory import get_llm_provider


class NLPController(BaseController):
    def __init__(self):
        super().__init__()
        self.llm_provider = None

    def _get_llm_provider(self):
        if self.llm_provider is None:
            self.llm_provider = get_llm_provider()
        return self.llm_provider

    def _get_embeddings_provider(self):
        return self._get_llm_provider()

    async def _get_project_mongo_id(self, request, project_id: str):
        project_repo = ProjectRepository(request.app.db_client)
        project = await project_repo.find_one_by_project_id(project_id)
        if not project:
            return None
        return project["_id"]

    async def vectorize_project(self, request, project_id: str, do_reset: bool = False):
        project_mongo_id = await self._get_project_mongo_id(request, project_id)
        if not project_mongo_id:
            return {"success": False, "message": "Project not found"}

        data_chunk_repo = DataChunkRepository(request.app.db_client)

        result = await data_chunk_repo.get_project_chunks(
            project_mongo_id, page=1, limit=10000
        )
        project_chunks = result.get("chunks", [])

        if not project_chunks or len(project_chunks) == 0:
            return {"success": False, "message": "No chunks found for this project"}

        collection_name = f"project_{project_id}"

        qdrant_provider = QDrantProvider(
            db_path=request.app.state.settings.VECTOR_DB_PATH,
            distance_method=request.app.state.settings.VECTOR_DISTANCE_METRIC,
        )
        await qdrant_provider.vectorDB_connection()

        embedding_model = request.app.state.settings.EMBEDDING_MODEL
        embedding_size = request.app.state.settings.EMBEDDING_MODEL_SIZE

        qdrant_provider.create_collection(
            collection_name=collection_name,
            embedding_size=embedding_size,
            do_reset=do_reset,
        )

        llm = self._get_llm_provider()
        llm.set_embedding_model(embedding_model, embedding_size)

        texts = []
        vectors = []
        metadatas = []

        for chunk in project_chunks:
            texts.append(chunk["chunk_text"])
            metadatas.append(chunk.get("chunk_metadata", {}))

            vector = llm.embed_text(chunk["chunk_text"], embedding_type="document")
            vectors.append(vector)

        qdrant_provider.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadata=metadatas,
        )

        return {
            "success": True,
            "message": f"Vectorized {len(texts)} chunks successfully",
            "chunks_count": len(texts),
            "collection_name": collection_name,
        }

    async def get_vectorization_info(self, request, project_id: str):
        collection_name = f"project_{project_id}"

        qdrant_provider = QDrantProvider(
            db_path=request.app.state.settings.VECTOR_DB_PATH,
            distance_method=request.app.state.settings.VECTOR_DISTANCE_METRIC,
        )
        await qdrant_provider.vectorDB_connection()

        if not qdrant_provider.is_collection_exists(collection_name):
            return {
                "success": False,
                "message": "Collection does not exist",
                "vectorized": False,
            }

        collection_info = qdrant_provider.get_collection_info(collection_name)

        return {
            "success": True,
            "vectorized": True,
            "collection_name": collection_name,
            "vectors_count": getattr(collection_info, "vectors_count", 0),
            "points_count": getattr(collection_info, "points_count", 0),
            "status": getattr(collection_info, "status", "unknown"),
        }

    async def get_similar_vectors(
        self, request, project_id: str, query_text: str, limit: int = 5
    ):
        collection_name = f"project_{project_id}"

        qdrant_provider = QDrantProvider(
            db_path=request.app.state.settings.VECTOR_DB_PATH,
            distance_method=request.app.state.settings.VECTOR_DISTANCE_METRIC,
        )
        await qdrant_provider.vectorDB_connection()

        if not qdrant_provider.is_collection_exists(collection_name):
            return {"success": False, "message": "Collection does not exist"}

        llm = self._get_llm_provider()
        query_vector = llm.embed_text(query_text, embedding_type="query")

        results = qdrant_provider.search_by_vector(
            collection_name=collection_name, vector=query_vector, limit=limit
        )

        similar_docs = []
        for result in results:
            similar_docs.append(
                {
                    "text": result.payload.get("text", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "score": result.score,
                }
            )

        return {
            "success": True,
            "query": query_text,
            "results": similar_docs,
            "results_count": len(similar_docs),
        }

    async def answer_user_question(
        self,
        request,
        project_id: str,
        question: str,
        limit: int = 5,
        max_output_token: Optional[int] = None,
        temperature: Optional[float] = None,
    ):
        project_mongo_id = await self._get_project_mongo_id(request, project_id)
        if not project_mongo_id:
            return {"success": False, "message": "Project not found"}

        collection_name = f"project_{project_id}"

        qdrant_provider = QDrantProvider(
            db_path=request.app.state.settings.VECTOR_DB_PATH,
            distance_method=request.app.state.settings.VECTOR_DISTANCE_METRIC,
        )
        await qdrant_provider.vectorDB_connection()

        if not qdrant_provider.is_collection_exists(collection_name):
            return {
                "success": False,
                "message": "Collection does not exist - please vectorize the project first",
            }

        gen_llm = self._get_llm_provider()
        gen_llm.set_model(request.app.state.settings.GENERATION_MODEL)

        emb_llm = self._get_embeddings_provider()
        emb_llm.set_embedding_model(
            request.app.state.settings.EMBEDDING_MODEL,
            request.app.state.settings.EMBEDDING_MODEL_SIZE,
        )

        query_vector = emb_llm.embed_text(question, embedding_type="query")

        results = qdrant_provider.search_by_vector(
            collection_name=collection_name, vector=query_vector, limit=limit
        )

        if not results or len(results) == 0:
            system_prompt = "You are a helpful AI assistant. Be polite and helpful."
            user_prompt = (
                f"The user asked: '{question}'. "
                "Apologize and explain that no relevant information was found in the available documents to answer their question. "
                "Suggest they may need to add more documents or vectorize the project first."
            )
            answer = gen_llm.generate_text(
                prompt=user_prompt,
                max_output_token=max_output_token,
                temperature=temperature,
                system_prompt=system_prompt,
            )
            return {
                "success": True,
                "question": question,
                "answer": answer,
                "sources": [],
                "sources_count": 0,
            }

        retrieved_documents = []
        context_parts = []

        for idx, result in enumerate(results):
            text = result.payload.get("text", "")
            metadata = result.payload.get("metadata", {})
            score = result.score

            retrieved_documents.append(
                {"text": text, "metadata": metadata, "score": score, "rank": idx + 1}
            )

            context_parts.append(f"[Document {idx + 1}]:\n{text}")

        context = "\n\n".join(context_parts)

        system_prompt = """You are a helpful AI assistant specialized in answering questions based on provided documents.
                        Your instructions:
                        1. Answer ONLY based on the context provided below
                        2. If the answer cannot be found in the context, clearly state that you don't have enough information
                        3. Be specific and reference relevant details from the context
                        4. If there are multiple relevant pieces of information, provide a comprehensive answer
                        5. Always be polite and helpful"""

        user_prompt = f"""Context from documents:
                    ---
                    {context}
                    ---

                    User Question: {question}

                    Your Answer:"""

        generated_answer = gen_llm.generate_text(
            prompt=user_prompt,
            max_output_token=max_output_token,
            temperature=temperature,
            system_prompt=system_prompt,
        )

        return {
            "success": True,
            "question": question,
            "answer": generated_answer,
            "sources": retrieved_documents,
            "sources_count": len(retrieved_documents),
            "collection_name": collection_name,
        }