import os
import random
import time

from chromadb.utils import embedding_functions
from google import genai
from google.genai.errors import ClientError
from langchain.embeddings.base import Embeddings


def _es_error_cuota(exc: Exception) -> bool:
    if isinstance(exc, ClientError):
        if exc.code == 429:
            return True
        if exc.code == 500 and "RESOURCE_EXHAUSTED" in str(exc).upper():
            return True
    mensaje = str(exc).upper()
    return "RESOURCE_EXHAUSTED" in mensaje or "429" in mensaje or "QUOTA" in mensaje or "RATE_LIMIT" in mensaje


class GoogleGenAIEmbeddings(Embeddings):
    _MAX_BATCH_SIZE = int(os.getenv("GOOGLE_GENAI_EMBEDDING_BATCH_SIZE", "1"))
    _BATCH_DELAY_SECONDS = float(os.getenv("GOOGLE_GENAI_EMBEDDING_DELAY", "2.0"))
    _MAX_RETRIES = int(os.getenv("GOOGLE_GENAI_EMBEDDING_MAX_RETRIES", "10"))

    def __init__(self, api_key: str, model: str = "gemini-embedding-2-preview"):
        if not api_key:
            raise ValueError("Debe proporcionar una API key de Google GenAI para inicializar el cliente.")

        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._fallback_embeddings = None

        if os.getenv("USE_LOCAL_EMBEDDINGS", "0").lower() in {"1", "true", "yes", "on"}:
            try:
                self._fallback_embeddings = embedding_functions.DefaultEmbeddingFunction()
            except Exception:
                self._fallback_embeddings = None

    def _embed_batch(self, batch: list[str]) -> list[list[float]]:
        response = self._client.models.embed_content(
            model=self._model,
            contents=batch,
        )
        if not response.embeddings:
            raise ValueError("No se devolvieron embeddings de Google GenAI en el lote.")
        resultado = []
        for embedding in response.embeddings:
            if embedding.values is None:
                raise ValueError("Respuesta de embedding incompleta: valores faltantes.")
            resultado.append(list(embedding.values))
        return resultado

    def _embed_batch_with_retry(self, batch: list[str]) -> list[list[float]]:
        last_exc = None
        for attempt in range(self._MAX_RETRIES):
            try:
                return self._embed_batch(batch)
            except Exception as exc:
                last_exc = exc
                if not _es_error_cuota(exc):
                    raise
                if attempt == self._MAX_RETRIES - 1:
                    break
                delay = min(2 ** (attempt + 2), 60.0) + random.uniform(0, 1)
                tipo = "cuota excedida"
                print(f"Error {tipo}. Reintentando en {delay:.1f}s (intento {attempt + 1}/{self._MAX_RETRIES})...")
                time.sleep(delay)
                continue

        if self._fallback_embeddings is not None:
            try:
                return self._fallback_embeddings(batch)
            except Exception:
                pass
        raise RuntimeError(
            f"Error de Google GenAI al generar embeddings con el modelo '{self._model}' "
            f"tras {self._MAX_RETRIES} intentos. "
            f"Verifique su clave, cuota y configuración de modelo. "
            f"Último error: {last_exc}"
        ) from last_exc

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings: list[list[float]] = []
        for start in range(0, len(texts), self._MAX_BATCH_SIZE):
            batch = texts[start : start + self._MAX_BATCH_SIZE]
            embeddings.extend(self._embed_batch_with_retry(batch))
            time.sleep(self._BATCH_DELAY_SECONDS)
        return embeddings

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed_texts(texts)

    def embed_query(self, text: str) -> list[float]:
        resultado = self._embed_texts([text])
        return resultado[0] if resultado else []
