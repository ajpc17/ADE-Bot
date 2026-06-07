# Arquitectura del sistema — ADE-Bot

## 1. Diagrama general

```mermaid
graph TD
    U([Usuario]) -->|mensaje| WEB[Interfaz Web]
    WEB -->|POST /api/chat| FA[FastAPI - main.py]
    FA --> CS[ChatService]

    CS -->|texto de consulta| EM[Embeddings\ntext-embedding-004]
    EM -->|vector| VDB[(ChromaDB)]
    VDB -->|fragmentos relevantes| PR[Constructor de prompt]
    PR -->|prompt + contexto| LLM[Gemini 2.5 Pro]
    LLM -->|respuesta| CS
    CS -->|respuesta| FA
    FA -->|JSON| WEB

    CS -->|log| SQ[(SQLite)]

    WEB -->|POST /api/upload| FA
    FA -->|texto extraído| CS

    DOC[PDFs oficiales\n/datos] --> ING[Pipeline de ingesta\ningesta/ingest.py]
    ING --> EMI[Embeddings offline]
    EMI --> VDB
```

---

## 2. Flujo de una consulta

```mermaid
sequenceDiagram
    participant U as Usuario
    participant WEB as Interfaz Web
    participant FA as FastAPI
    participant CS as ChatService
    participant VDB as ChromaDB
    participant GEM as Gemini API
    participant SQ as SQLite

    U->>WEB: escribe una pregunta
    WEB->>FA: POST /api/chat {mensaje, session_id}
    FA->>CS: procesar_consulta(texto, user_id, contexto_extra)
    CS->>VDB: buscar(texto, top_k=4, threshold=0.75)
    VDB-->>CS: fragmentos con score ≥ 0.75
    CS->>CS: construir_prompt(fragmentos, contexto_extra)
    CS->>LLM: ainvoke(prompt) — Groq o Gemini según .env
    LLM-->>CS: respuesta en texto
    CS->>SQ: guardar(user_id, consulta, respuesta, resuelta)
    CS-->>FA: respuesta
    FA-->>WEB: {"respuesta": "..."}
    WEB-->>U: muestra la respuesta
```

---

## 3. Pipeline de ingesta (offline)

```mermaid
graph LR
    PDF[PDF en /datos] --> LOAD[PyPDFLoader]
    LOAD --> SPLIT[RecursiveCharacterTextSplitter\nchunk=800 / overlap=100]
    SPLIT --> META[Asignar metadata\ntema + fuente]
    META --> EMB[GoogleGenerativeAIEmbeddings\ntext-embedding-004]
    EMB --> CHROMA[(ChromaDB\n/db/chroma)]
```

El script detecta el tema del documento por el nombre del archivo (ver README).

---

## 4. Decisiones de diseño

**Proveedor de LLM configurable**
`main.py` expone `_crear_llm_client()`: si `GROQ_API_KEY` está definida en `.env`, instancia `GroqLLMClient` (llama-3.3-70b por defecto); si no, usa `GeminiLLMClient`. Cambiar de proveedor no requiere tocar `ChatService`.

**Inyección de dependencias en `ChatService`**
`ChatService` recibe `VectorStore`, `LLMClient` y `LogRepository` como interfaces abstractas. Esto permite sustituirlos por fakes en las pruebas del Módulo 4 sin conexión a ningún proveedor externo.

**Contexto de sesión en memoria**
Los PDFs adjuntados por el usuario se almacenan en `_session_docs` (dict en proceso). Se pierden al reiniciar el servidor. No se persisten por diseño — son contexto temporal de la sesión.

**Fallback sin contexto**
Si ChromaDB no retorna fragmentos con score ≥ threshold y no hay documentos adjuntos, el sistema usa un prompt alternativo que indica al bot responder desde conocimiento general y aclarar que la respuesta no proviene de documentos oficiales.

**Threshold de similitud**
Un valor de 0.75 filtra fragmentos poco relacionados y reduce respuestas alucinadas. Si los PDFs no están ingestados, todas las búsquedas regresan vacías y el bot activa el fallback.
