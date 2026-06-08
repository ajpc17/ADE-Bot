from infrastructure.vector_store import VectorStore
from infrastructure.llm_client import LLMClient
from infrastructure.log_repository import LogRepository

_SYSTEM_PROMPT = (
    "Eres Juanito el Inge, asistente institucional del Área de Ingeniería en Diseño. "
    "Tu tono debe ser formal, claro, amable e institucional. "
    "Responde únicamente con información respaldada por los documentos oficiales recuperados. "
    "Si usas información recuperada, cita cada fuente explícitamente en el formato [Fuente: nombre_documento.ext]. "
    "Si empleas varias fuentes, menciona todas las fuentes utilizadas. "
    "No agregues contenido que no esté presente en el contexto proporcionado. "
    "Interpreta correctamente la jerga estudiantil, por ejemplo: 'que vaina' puede referirse a un trámite, 'blueprint' a un plano, 'pa pedir un permiso' a un procedimiento administrativo. "
    "Si la pregunta está fuera del alcance del Área de Ingeniería en Diseño o no hay contenido recuperado suficiente, rechaza la consulta de forma protocolar y amable."
)


class ChatService:
    def __init__(
        self,
        vector_store: VectorStore,
        llm_client: LLMClient,
        log_repository: LogRepository,
        top_k: int = 4,
        similarity_threshold: float = 0.60,
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
        print(f"[DEBUG] ChatService.procesar_consulta texto={texto!r} top_k={self._top_k} threshold={self._threshold}")
        # Forzamos threshold a 0.0 para ignorar el filtro matemático defectuoso
        fragmentos = await self._vector_store.buscar(texto, self._top_k, 0.0) 
        print(f"[DEBUG] ChatService received {len(fragmentos)} fragmentos")
        if not fragmentos and not contexto_extra:
            respuesta = (
                "Lo siento, soy Juanito el Inge y no puedo responder esa consulta porque no corresponde al área de Ingeniería en Diseño "
                "o no se obtuvo información suficiente de los documentos oficiales disponibles. "
                "Por favor, formula una pregunta específica relacionada con trámites, planos, materiales o normas del área."
            )
            await self._logs.guardar(user_id, texto, respuesta, resuelta=False)
            return respuesta

        prompt = self._construir_prompt(texto, fragmentos, contexto_extra)
        respuesta = await self._llm.generar(prompt)
        await self._logs.guardar(user_id, texto, respuesta, resuelta=bool(fragmentos or contexto_extra))
        return respuesta

    def _construir_prompt(
        self,
        consulta: str,
        fragmentos: list[str],
        contexto_extra: str = "",
    ) -> str:
        partes = []
        if fragmentos:
            partes.append("Documentos oficiales recuperados:\n" + "\n\n".join(fragmentos))
        if contexto_extra:
            partes.append("Documentos cargados en la sesión:\n" + contexto_extra)
        contexto = "\n\n---\n\n".join(partes)
        return (
            f"{_SYSTEM_PROMPT}\n\n"
            f"Contexto:\n{contexto}\n\n"
            f"Pregunta: {consulta}\n"
            f"Respuesta:"
        )
