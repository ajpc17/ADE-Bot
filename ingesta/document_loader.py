from __future__ import annotations

import io
import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from PIL import Image
from docx import Document as DocxDocument

try:
    import pytesseract
except ImportError:  # pragma: no cover
    pytesseract = None


TEXT_EXTENSIONS = {".txt", ".docx", ".pdf"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
THREED_EXTENSIONS = {".glb", ".gltf", ".obj"}

DEFAULT_CHUNK_SIZE = int(os.getenv("INGEST_CHUNK_SIZE", "2000"))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("INGEST_CHUNK_OVERLAP", "250"))


def _get_splitter(chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def _split_text(text: str, filename: str) -> list[Document]:
    doc = Document(page_content=text, metadata={"fuente": filename})
    return _get_splitter().split_documents([doc])


def _cargar_pdf_desde_bytes(contenido: bytes, filename: str) -> list[Document]:
    """Extrae texto de un PDF en memoria usando pypdf."""
    reader = PdfReader(io.BytesIO(contenido))
    paginas: list[Document] = []
    for numero, pagina in enumerate(reader.pages, start=1):
        texto = pagina.extract_text() or ""
        if texto.strip():
            paginas.append(Document(
                page_content=texto.strip(),
                metadata={"fuente": filename, "pagina": numero},
            ))
    if not paginas:
        return []
    return _get_splitter().split_documents(paginas)


def _cargar_txt_desde_bytes(contenido: bytes, filename: str) -> list[Document]:
    texto = contenido.decode("utf-8", errors="replace")
    return _split_text(texto, filename)


def _cargar_docx_desde_bytes(contenido: bytes, filename: str) -> list[Document]:
    doc = DocxDocument(io.BytesIO(contenido))
    parrafos = [p.text for p in doc.paragraphs if p.text.strip()]
    return _split_text("\n".join(parrafos), filename)


def _cargar_imagen_desde_bytes(contenido: bytes, filename: str) -> list[Document]:
    try:
        imagen = Image.open(io.BytesIO(contenido))
        metadata = {k: str(v) for k, v in imagen.info.items() if v}
        ocr_text = ""
        if pytesseract is not None:
            try:
                ocr_text = pytesseract.image_to_string(imagen)
            except Exception:
                ocr_text = ""
        texto = (
            f"Imagen: {filename}. Metadata: {metadata or 'sin metadata'}."
            f"\n\nTexto detectado: {ocr_text.strip() or 'No se detectó texto legible.'}"
        )
        return _split_text(texto, filename)
    except Exception:
        return [Document(page_content=f"Imagen {filename} no pudo procesarse.", metadata={"fuente": filename})]


def _cargar_modelo_3d(referencia: str, titulo: str | None = None, descripcion: str | None = None) -> list[Document]:
    cuerpo = [
        f"Modelo 3D: {titulo or referencia}",
        f"Referencia: {referencia}",
        f"Descripción: {descripcion or 'Recurso 3D de ingeniería de diseño.'}",
        "Elemento interactivo de diseño relacionado con materiales, planos o modelado 3D.",
    ]
    return _split_text("\n".join(cuerpo), referencia)


# ---------------------------------------------------------------------------
# Punto de entrada: archivos en disco (usado por ingesta offline)
# ---------------------------------------------------------------------------

def cargar_documento(path: Path) -> list[Document]:
    """Carga un archivo desde disco y retorna fragmentos listos para indexar."""
    extension = path.suffix.lower()
    contenido = path.read_bytes()

    if extension == ".pdf":
        return _cargar_pdf_desde_bytes(contenido, path.name)
    if extension == ".txt":
        return _cargar_txt_desde_bytes(contenido, path.name)
    if extension == ".docx":
        return _cargar_docx_desde_bytes(contenido, path.name)
    if extension in IMAGE_EXTENSIONS:
        return _cargar_imagen_desde_bytes(contenido, path.name)
    if extension in THREED_EXTENSIONS:
        return _cargar_modelo_3d(path.name, descripcion="Archivo 3D de referencia para ingeniería de diseño.")
    raise ValueError(f"Formato no soportado para la ingesta: {extension}")


# ---------------------------------------------------------------------------
# Punto de entrada: bytes en memoria (usado por uploads de sesión en /api/upload)
# ---------------------------------------------------------------------------

def cargar_documento_desde_bytes(filename: str, content: bytes) -> list[Document]:
    """Carga un archivo desde bytes (subido vía API) y retorna fragmentos."""
    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        return _cargar_pdf_desde_bytes(content, filename)
    if extension == ".txt":
        return _cargar_txt_desde_bytes(content, filename)
    if extension == ".docx":
        return _cargar_docx_desde_bytes(content, filename)
    if extension in IMAGE_EXTENSIONS:
        return _cargar_imagen_desde_bytes(content, filename)
    if extension in THREED_EXTENSIONS:
        return _cargar_modelo_3d(filename, descripcion="Archivo 3D de referencia para ingeniería de diseño.")
    raise ValueError(f"Formato no soportado para la ingesta: {extension}")
