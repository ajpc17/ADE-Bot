import os
import time

from google import genai
from google.genai.errors import ClientError
from langchain.embeddings.base import Embeddings


class GoogleGenAIEmbeddings(Embeddings):
    _MAX_BATCH_SIZE = int(os.getenv("GOOGLE_GENAI_EMBEDDING_BATCH_SIZE", "25"))
    _BATCH_DELAY_SECONDS = float(os.getenv("GOOGLE_GENAI_EMBEDDING_DELAY", "0.2"))

    def __init__(self, api_key: str, model: str = "gemini-embedding-001"):
        if not api_key:
            raise ValueError("Debe proporcionar una API key de Google GenAI para inicializar el cliente.")

        # Limpiar cualquier residuo de formato de cadena antiguo
        if model.startswith("models/"):
            model_limpio = model.replace("models/", "")
        else:
            model_limpio = model

        # CORRECCIÓN DE DEPRECACIÓN: Mapeamos los modelos antiguos o experimentales 
        # al nuevo modelo mainline global 'gemini-embedding-001' soportado por el backend.
        if model_limpio in ["text-embedding-004", "gemini-embedding-2-preview"] or "gemini" not in model_limpio:
            self._model = "gemini-embedding-001"
        else:
            self._model = model_limpio

        self._client = genai.Client(api_key=api_key)

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        embeddings: list[list[float]] = []
        for start in range(0, len(texts), self._MAX_BATCH_SIZE):
            batch = texts[start : start + self._MAX_BATCH_SIZE]
            try:
                response = self._client.models.embed_content(
                    model=self._model,
                    contents=batch,
                )
            except ClientError as exc:
                raise RuntimeError(
                    f"Error de Google GenAI al generar embeddings con el modelo '{self._model}'. "
                    "Verifique su clave, cuota y configuración de modelo. "
                    f"Mensaje original: {exc}"
                ) from exc

            if not response.embeddings:
                raise ValueError("No se devolvieron embeddings de Google GenAI en el lote.")

            for embedding in response.embeddings:
                if embedding.values is None:
                    raise ValueError("Respuesta de embedding incompleta: valores faltantes.")
                
                # Conversión estricta a tipos primitivos float de Python para evitar desajustes en Chroma
                vector_flotante = [float(x) for x in embedding.values]
                embeddings.append(vector_flotante)

            time.sleep(self._BATCH_DELAY_SECONDS)

        return embeddings

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed_texts(texts)

    def embed_query(self, text: str) -> list[float]:
        resultado = self._embed_texts([text])
        if not resultado:
            raise ValueError(f"No se pudo generar el embedding de consulta para el texto: {text}")
        return resultado[0]