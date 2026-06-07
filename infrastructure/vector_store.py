from abc import ABC, abstractmethod

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings


class VectorStore(ABC):
    @abstractmethod
    async def buscar(self, consulta: str, top_k: int, threshold: float) -> list[str]:
        pass


class ChromaVectorStore(VectorStore):
    def __init__(self, path: str, api_key: str):
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=api_key,
        )
        self._db = Chroma(persist_directory=path, embedding_function=embeddings)

    async def buscar(self, consulta: str, top_k: int, threshold: float) -> list[str]:
        try:
            resultados = self._db.similarity_search_with_relevance_scores(consulta, k=top_k)
        except Exception:
            return []
        return [doc.page_content for doc, score in resultados if score >= threshold]
