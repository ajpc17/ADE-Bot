import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ingesta.document_loader import cargar_documento_desde_bytes
from infrastructure.llm_client import GeminiLLMClient, GroqLLMClient
from infrastructure.log_repository import SQLiteLogRepository
from infrastructure.vector_store import ChromaVectorStore
from services.chat_service import ChatService
from services.session_store import SessionDocumentStore

load_dotenv()

DEFAULT_CHROMA_PATH = "./db/chroma"
DEFAULT_SQLITE_PATH = "./db/logs.db"
ALLOWED_FILE_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg",
    ".glb",
    ".gltf",
    ".obj",
}

session_store = SessionDocumentStore()


class MensajeRequest(BaseModel):
    mensaje: str
    session_id: str = "anonimo"


class Modelo3DReference(BaseModel):
    session_id: str = "anonimo"
    referencia: str
    titulo: str | None = None
    descripcion: str | None = None


def _crear_llm_client() -> GeminiLLMClient | GroqLLMClient:
    groq_key = os.getenv("GROQ_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    if groq_key:
        return GroqLLMClient(
            api_key=groq_key,
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        )
    if gemini_key:
        return GeminiLLMClient(
            api_key=gemini_key,
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
        )
    raise RuntimeError(
        "Debe configurar GROQ_API_KEY o GEMINI_API_KEY en el entorno antes de iniciar la aplicación."
    )


def _obtener_chroma_api_key() -> str:
    return os.getenv("CHROMA_API_KEY") or os.getenv("GEMINI_API_KEY") or ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    chroma_path = os.getenv("CHROMA_PATH", DEFAULT_CHROMA_PATH)
    sqlite_path = os.getenv("SQLITE_PATH", DEFAULT_SQLITE_PATH)
    Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    Path(chroma_path).mkdir(parents=True, exist_ok=True)

    vector_store = ChromaVectorStore(
        path=chroma_path,
        api_key=_obtener_chroma_api_key(),
        model="gemini-embedding-001",
    )
    llm_client = _crear_llm_client()
    log_repository = SQLiteLogRepository(path=sqlite_path)

    app.state.chat_service = ChatService(
        vector_store=vector_store,
        llm_client=llm_client,
        log_repository=log_repository,
        top_k=int(os.getenv("TOP_K", 4)),
        similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", 0.60)),
    )
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.post("/api/chat")
async def chat(request: MensajeRequest):
    contexto_extra = await session_store.format_context(request.session_id)
    user_id = abs(hash(request.session_id)) % (2 ** 31)
    respuesta = await app.state.chat_service.procesar_consulta(
        texto=request.mensaje,
        user_id=user_id,
        contexto_extra=contexto_extra,
    )
    return {"respuesta": respuesta}


@app.get("/api/fuentes")
async def fuentes(session_id: str = "anonimo"):
    documentos = await session_store.list(session_id)
    return {
        "archivos": [
            {
                "filename": documento.filename,
                "resource_type": documento.resource_type,
                "metadata": documento.metadata,
            }
            for documento in documentos
        ]
    }


@app.post("/api/upload")
async def upload(archivo: UploadFile = File(...), session_id: str = Form("anonimo")):
    extension = Path(archivo.filename).suffix.lower()
    if extension not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="Formato no soportado. Solo se aceptan PDF, TXT, DOCX, PNG, JPG, JPEG, GLB, GLTF y OBJ.",
        )

    contenido = await archivo.read()
    try:
        documentos = cargar_documento_desde_bytes(archivo.filename, contenido)
    except ValueError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc

    if not documentos:
        raise HTTPException(
            status_code=422,
            detail=f"No se pudo extraer texto o metadatos del archivo {archivo.filename}.",
        )

    chunks = [document.page_content for document in documentos]
    resource_type = "modelo_3d" if extension in {".glb", ".gltf", ".obj"} else "imagen" if extension in {".png", ".jpg", ".jpeg"} else "documento"
    await session_store.add(
        session_id=session_id,
        filename=archivo.filename,
        chunks=chunks,
        resource_type=resource_type,
        metadata={"fuente": archivo.filename},
    )

    return {"archivo": archivo.filename, "fragmentos": len(chunks), "resource_type": resource_type}


@app.post("/api/resource/3d")
async def registrar_modelo_3d(request: Modelo3DReference):
    referencia = request.referencia.strip()
    if not referencia:
        raise HTTPException(status_code=422, detail="La referencia 3D es obligatoria.")

    filename = f"3D:{request.titulo or referencia}"
    chunks = [
        f"Modelo 3D: {request.titulo or referencia}",
        f"Referencia: {referencia}",
        f"Descripción: {request.descripcion or 'Recurso 3D relacionado con el área de Ingeniería en Diseño.'}",
        "Este recurso debe considerarse un elemento interactivo de diseño y materiales.",
    ]
    await session_store.add(
        session_id=request.session_id,
        filename=filename,
        chunks=chunks,
        resource_type="modelo_3d",
        metadata={"referencia": referencia, "titulo": request.titulo or "n/a"},
    )
    return {"archivo": filename, "resource_type": "modelo_3d"}


@app.delete("/api/upload")
async def delete_upload(session_id: str, filename: str):
    await session_store.remove(session_id, filename)
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
