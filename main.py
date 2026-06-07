import io
import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pypdf import PdfReader

from infrastructure.llm_client import GeminiLLMClient, GroqLLMClient
from infrastructure.log_repository import SQLiteLogRepository
from infrastructure.vector_store import ChromaVectorStore
from services.chat_service import ChatService

load_dotenv()

Path(os.getenv("SQLITE_PATH", "./db/logs.db")).parent.mkdir(parents=True, exist_ok=True)

_chat_service: ChatService | None = None

# Documentos por sesion: {session_id: {filename: [paginas_texto]}}
_session_docs: dict[str, dict[str, list[str]]] = {}


def _crear_llm_client():
    if os.getenv("GROQ_API_KEY"):
        return GroqLLMClient(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        )
    return GeminiLLMClient(
        api_key=os.getenv("GEMINI_API_KEY"),
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _chat_service
    _chat_service = ChatService(
        vector_store=ChromaVectorStore(
            path=os.getenv("CHROMA_PATH"),
            api_key=os.getenv("GEMINI_API_KEY"),  # los embeddings siempre usan Google aunque el LLM sea Groq
        ),
        llm_client=_crear_llm_client(),
        log_repository=SQLiteLogRepository(
            path=os.getenv("SQLITE_PATH"),
        ),
        top_k=int(os.getenv("TOP_K", 4)),
        similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", 0.75)),
    )
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


class MensajeRequest(BaseModel):
    mensaje: str
    session_id: str = "anonimo"


def _extraer_texto_pdf(contenido: bytes) -> list[str]:
    reader = PdfReader(io.BytesIO(contenido))
    paginas = []
    for page in reader.pages:
        texto = page.extract_text()
        if texto and texto.strip():
            paginas.append(texto.strip())
    return paginas


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.post("/api/chat")
async def chat(request: MensajeRequest):
    session_docs = _session_docs.get(request.session_id, {})
    contexto_extra = ""
    if session_docs:
        partes = [
            f"[{fname}]\n" + "\n".join(chunks)
            for fname, chunks in session_docs.items()
        ]
        contexto_extra = "\n\n---\n\n".join(partes)

    user_id = abs(hash(request.session_id)) % (2 ** 31)
    respuesta = await _chat_service.procesar_consulta(
        texto=request.mensaje,
        user_id=user_id,
        contexto_extra=contexto_extra,
    )
    return {"respuesta": respuesta}


@app.get("/api/fuentes")
async def fuentes(session_id: str = "anonimo"):
    archivos = list(_session_docs.get(session_id, {}).keys())
    return {"archivos": archivos}


@app.post("/api/upload")
async def upload(
    archivo: UploadFile = File(...),
    session_id: str = Form("anonimo"),
):
    if not archivo.filename.lower().endswith(".pdf"):
        return JSONResponse({"error": "Solo se aceptan archivos PDF."}, status_code=400)

    contenido = await archivo.read()
    chunks = _extraer_texto_pdf(contenido)

    if not chunks:
        return JSONResponse({"error": "No se pudo extraer texto del PDF."}, status_code=422)

    if session_id not in _session_docs:
        _session_docs[session_id] = {}
    _session_docs[session_id][archivo.filename] = chunks

    return {"archivo": archivo.filename, "paginas": len(chunks)}


@app.delete("/api/upload")
async def delete_upload(session_id: str, filename: str):
    if session_id in _session_docs:
        _session_docs[session_id].pop(filename, None)
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
