import os
from abc import ABC, abstractmethod

from langchain_chroma import Chroma
from infrastructure.google_embeddings import GoogleGenAIEmbeddings
from starlette.concurrency import run_in_threadpool


class VectorStore(ABC):
    @abstractmethod
    async def buscar(self, consulta: str, top_k: int, threshold: float) -> list[str]:
        pass


class ChromaVectorStore(VectorStore):
    def __init__(self, path: str, api_key: str, model: str = "gemini-embedding-001"):
        embeddings = GoogleGenAIEmbeddings(
            api_key=api_key,
            model=model,
        )
        print(f"[DEBUG] ChromaVectorStore using embedding model: {model}")
        self._db = Chroma(persist_directory=path, embedding_function=embeddings)

    async def buscar(self, consulta: str, top_k: int, threshold: float) -> list[str]:
        print(f"[DEBUG] ChromaVectorStore.buscar query={consulta!r} top_k={top_k} threshold={threshold}")
        try:
            resultados = await run_in_threadpool(
                self._db.similarity_search_with_relevance_scores,
                consulta,
                k=top_k,
            )
        except Exception as exc:
            print("[DEBUG] Chroma search error:", repr(exc))
            return []

        print(f"[DEBUG] Chroma returned {len(resultados)} docs before threshold filtering")
        fragmentos = []
        for idx, (doc, score) in enumerate(resultados, start=1):
            fuente = doc.metadata.get("fuente") or doc.metadata.get("source") or "documento"
            print(f"[DEBUG]   hit {idx}: score={score:.6f} fuente={fuente}")
            if score < threshold:
                print(f"[DEBUG]   hit {idx} rejected by threshold")
                continue
            fragmentos.append(f"{doc.page_content}\n[Fuente: {fuente}]")

        print(f"[DEBUG] ChromaVectorStore.buscar returning {len(fragmentos)} fragmentos after threshold filtering")
        return fragmentos
