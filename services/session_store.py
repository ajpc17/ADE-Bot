<<<<<<< HEAD
import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SESSION_STORE_PATH = Path(os.getenv("SESSION_STORE_PATH", "./db/sessions"))
SESSION_STORE_PATH.mkdir(parents=True, exist_ok=True)
=======
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List
>>>>>>> upstream/master


@dataclass
class SessionDocument:
    filename: str
<<<<<<< HEAD
    chunks: list[str]
    resource_type: str
    metadata: dict[str, Any]

    @property
    def page_content(self) -> str:
        return "\n".join(self.chunks)
=======
    chunks: List[str]
    resource_type: str = "document"
    metadata: Dict[str, str] = field(default_factory=dict)
>>>>>>> upstream/master


class SessionDocumentStore:
    def __init__(self) -> None:
<<<<<<< HEAD
        self._storage_dir = SESSION_STORE_PATH

    def _session_file(self, session_id: str) -> Path:
        safe_id = session_id.replace("/", "_").replace("\\", "_")
        return self._storage_dir / f"{safe_id}.json"

    async def _read_session(self, session_id: str) -> list[dict[str, Any]]:
        path = self._session_file(session_id)
        if not path.exists():
            return []
        return await asyncio.to_thread(self._read_json, path)

    async def _write_session(self, session_id: str, data: list[dict[str, Any]]) -> None:
        path = self._session_file(session_id)
        await asyncio.to_thread(self._write_json, path, data)

    @staticmethod
    def _read_json(path: Path) -> list[dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def _write_json(path: Path, data: list[dict[str, Any]]) -> None:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)

    def _dict_to_document(self, document_data: dict[str, Any]) -> SessionDocument:
        return SessionDocument(
            filename=document_data["filename"],
            chunks=document_data["chunks"],
            resource_type=document_data["resource_type"],
            metadata=document_data.get("metadata", {}),
        )
=======
        self._documents: Dict[str, Dict[str, SessionDocument]] = {}
        self._lock = asyncio.Lock()
>>>>>>> upstream/master

    async def add(
        self,
        session_id: str,
        filename: str,
<<<<<<< HEAD
        chunks: list[str],
        resource_type: str,
        metadata: dict[str, Any],
    ) -> None:
        documents = await self._read_session(session_id)
        documents = [doc for doc in documents if doc.get("filename") != filename]
        documents.append(
            {
                "filename": filename,
                "chunks": chunks,
                "resource_type": resource_type,
                "metadata": metadata,
            }
        )
        await self._write_session(session_id, documents)

    async def list(self, session_id: str) -> list[SessionDocument]:
        documents = await self._read_session(session_id)
        return [self._dict_to_document(doc) for doc in documents]

    async def remove(self, session_id: str, filename: str) -> None:
        documents = await self._read_session(session_id)
        documents = [doc for doc in documents if doc.get("filename") != filename]
        await self._write_session(session_id, documents)

    async def format_context(self, session_id: str) -> str:
        documents = await self.list(session_id)
        chunks: list[str] = []
        for document in documents:
            chunks.extend(document.chunks)
        context = "\n".join(chunks)
        return context
=======
        chunks: List[str],
        resource_type: str = "document",
        metadata: Dict[str, str] | None = None,
    ) -> None:
        async with self._lock:
            if session_id not in self._documents:
                self._documents[session_id] = {}
            self._documents[session_id][filename] = SessionDocument(
                filename=filename,
                chunks=chunks,
                resource_type=resource_type,
                metadata=metadata or {},
            )

    async def get(self, session_id: str) -> Dict[str, SessionDocument]:
        async with self._lock:
            return dict(self._documents.get(session_id, {}))

    async def remove(self, session_id: str, filename: str) -> None:
        async with self._lock:
            if session_id in self._documents:
                self._documents[session_id].pop(filename, None)

    async def list(self, session_id: str) -> List[SessionDocument]:
        async with self._lock:
            return list(self._documents.get(session_id, {}).values())

    async def format_context(self, session_id: str) -> str:
        documentos = await self.get(session_id)
        if not documentos:
            return ""

        partes = []
        for documento in documentos.values():
            encabezado = f"[{documento.filename} | {documento.resource_type}]"
            partes.append(encabezado + "\n" + "\n".join(documento.chunks))
        return "\n\n---\n\n".join(partes)
>>>>>>> upstream/master
