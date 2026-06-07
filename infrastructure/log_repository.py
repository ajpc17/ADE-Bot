import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime


class LogRepository(ABC):
    @abstractmethod
    async def guardar(self, user_id: int, consulta: str, respuesta: str | None, resuelta: bool) -> None:
        pass


class SQLiteLogRepository(LogRepository):
    def __init__(self, path: str):
        self._path = path
        self._crear_tabla()

    def _crear_tabla(self) -> None:
        with sqlite3.connect(self._path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id   INTEGER NOT NULL,
                    consulta  TEXT    NOT NULL,
                    respuesta TEXT,
                    resuelta  INTEGER NOT NULL,
                    fecha     TEXT    NOT NULL
                )
            """)

    async def guardar(self, user_id: int, consulta: str, respuesta: str | None, resuelta: bool) -> None:
        with sqlite3.connect(self._path) as conn:
            conn.execute(
                "INSERT INTO logs (user_id, consulta, respuesta, resuelta, fecha) VALUES (?, ?, ?, ?, ?)",
                (user_id, consulta, respuesta, int(resuelta), datetime.now().isoformat()),
            )
