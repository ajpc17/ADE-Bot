import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

_ETIQUETAS = {
    "pensum":     "Pensum y Materias",
    "licitacion": "Licitaciones y Contratos",
    "proceso":    "Tramites Administrativos",
    "plano":      "Normas de Diseno",
    "financiero": "Presupuesto y Finanzas",
    "seguridad":  "Seguridad en Obras",
}


def _detectar_etiqueta(nombre: str) -> str:
    nombre_lower = nombre.lower()
    for clave, etiqueta in _ETIQUETAS.items():
        if clave in nombre_lower:
            return etiqueta
    return "General"


def ejecutar(docs_path: str | None = None) -> None:
    datos_path = Path(docs_path) if docs_path else Path("datos")
    pdfs = list(datos_path.glob("*.pdf"))

    if not pdfs:
        print(f"No se encontraron PDFs en {datos_path}/")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )

    fragmentos_totales = []

    for pdf in pdfs:
        print(f"Procesando: {pdf.name}")
        loader = PyPDFLoader(str(pdf))
        documentos = loader.load()
        fragmentos = splitter.split_documents(documentos)
        etiqueta = _detectar_etiqueta(pdf.stem)

        for frag in fragmentos:
            frag.metadata["tema"] = etiqueta
            frag.metadata["fuente"] = pdf.name

        fragmentos_totales.extend(fragmentos)
        print(f"  {len(fragmentos)} fragmentos generados [{etiqueta}]")

    chroma_path = os.getenv("CHROMA_PATH")
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)

    Chroma.from_documents(
        documents=fragmentos_totales,
        embedding=embeddings,
        persist_directory=chroma_path,
    )

    print(f"\nIngesta completada. {len(fragmentos_totales)} fragmentos indexados.")


if __name__ == "__main__":
    ejecutar()
