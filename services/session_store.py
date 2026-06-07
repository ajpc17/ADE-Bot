from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SessionDocument:
    filename: str
    chunks: List[str]
    resource_type: str = "document"
    metadata: Dict[str, str] = field(default_factory=dict)


class SessionDocumentStore:
    def __init__(self) -> None:
        self._documents: Dict[str, Dict[str, SessionDocument]] = {}
        self._lock = asyncio.Lock()

    async def add(
        self,
        session_id: str,
        filename: str,
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
