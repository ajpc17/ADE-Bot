from infrastructure.vector_store import VectorStore
from infrastructure.llm_client import LLMClient
from infrastructure.log_repository import LogRepository

_PROMPT_CON_CONTEXTO = (
    "Eres Juanito el Inge, el asistente del area de Ingenieria en Diseno. "
    "Responde de forma clara, formal y amable. "
    "Usa unicamente la informacion del contexto proporcionado. "
    "No menciones el origen de la informacion ni hagas aclaraciones sobre fuentes o documentos. "
    "Evita repetir innecesariamente el nombre del tema que ya quedo establecido en la pregunta. "
    "Usa negrita (**texto**) para resaltar terminos tecnicos clave."
)

_PROMPT_SIN_CONTEXTO = (
    "Eres Juanito el Inge, el asistente del area de Ingenieria en Diseno. "
    "Responde de forma clara y amable usando tu conocimiento general sobre ingenieria en diseno. "
    "No hagas aclaraciones sobre el origen de la informacion ni menciones documentos. "
    "Evita repetir innecesariamente el nombre del tema que ya quedo establecido en la pregunta. "
    "Usa negrita (**texto**) para resaltar terminos tecnicos clave."
)


class ChatService:
    def __init__(
        self,
        vector_store: VectorStore,
        llm_client: LLMClient,
        log_repository: LogRepository,
        top_k: int = 4,
        similarity_threshold: float = 0.75,
    ):
        self._vector_store = vector_store
        self._llm = llm_client
        self._logs = log_repository
        self._top_k = top_k
        self._threshold = similarity_threshold

    async def procesar_consulta(
        self,
        texto: str,
        user_id: int,
        contexto_extra: str = "",
    ) -> str:
        fragmentos = await self._vector_store.buscar(texto, self._top_k, self._threshold)
        hay_contexto = bool(fragmentos or contexto_extra)

        prompt = self._construir_prompt(texto, fragmentos, contexto_extra, hay_contexto)
        respuesta = await self._llm.generar(prompt)
        await self._logs.guardar(user_id, texto, respuesta, resuelta=hay_contexto)
        return respuesta

    def _construir_prompt(
        self,
        consulta: str,
        fragmentos: list[str],
        contexto_extra: str = "",
        hay_contexto: bool = True,
    ) -> str:
        sistema = _PROMPT_CON_CONTEXTO if hay_contexto else _PROMPT_SIN_CONTEXTO
        if hay_contexto:
            partes = []
            if fragmentos:
                partes.append("Base de conocimiento:\n" + "\n\n".join(fragmentos))
            if contexto_extra:
                partes.append("Documentos de la sesion:\n" + contexto_extra)
            contexto = "\n\n---\n\n".join(partes)
            return (
                f"{sistema}\n\n"
                f"Contexto:\n{contexto}\n\n"
                f"Pregunta: {consulta}\n"
                f"Respuesta:"
            )
        return (
            f"{sistema}\n\n"
            f"Pregunta: {consulta}\n"
            f"Respuesta:"
        )
