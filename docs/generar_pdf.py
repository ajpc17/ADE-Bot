from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-12)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 8, f"ADE-Bot  |  Documentacion del Proyecto  |  Pagina {self.page_no()}", align="C")
            self.set_text_color(0, 0, 0)

    def portada(self):
        self.add_page()
        self.set_fill_color(37, 99, 235)
        self.rect(0, 0, 210, 297, "F")
        self.set_y(80)
        self.set_font("Helvetica", "B", 52)
        self.set_text_color(255, 255, 255)
        self.cell(0, 20, "ADE-Bot", align="C", ln=True)
        self.set_font("Helvetica", "", 18)
        self.set_text_color(186, 213, 255)
        self.cell(0, 10, "Documentacion del Proyecto", align="C", ln=True)
        self.ln(10)
        self.set_font("Helvetica", "", 13)
        self.set_text_color(219, 234, 254)
        self.cell(0, 8, "Chatbot institucional para el Area de Ingenieria en Diseno", align="C", ln=True)
        self.ln(40)
        self.set_font("Helvetica", "I", 11)
        self.set_text_color(186, 213, 255)
        self.cell(0, 8, "Universidad  |  Ingenieria en Diseno  |  2026", align="C", ln=True)

    def nueva_seccion(self, n, titulo):
        self.add_page()
        self.set_fill_color(37, 99, 235)
        self.rect(0, 0, 210, 18, "F")
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(255, 255, 255)
        self.set_xy(0, 3)
        self.cell(0, 12, f"  {n}.  {titulo}", ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def subtitulo(self, texto):
        self.ln(4)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(37, 99, 235)
        self.cell(0, 7, texto, ln=True)
        self.set_draw_color(37, 99, 235)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(2)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)

    def parrafo(self, texto):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(55, 65, 81)
        self.set_x(self.l_margin)
        self.multi_cell(190, 5.5, texto)
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def item(self, texto):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(55, 65, 81)
        self.set_x(14)
        self.cell(4, 5.5, chr(149))
        self.set_x(18)
        self.multi_cell(182, 5.5, texto)
        self.set_text_color(0, 0, 0)

    def item_num(self, n, texto):
        self.set_font("Helvetica", "B", 10)
        self.set_x(14)
        self.cell(6, 5.5, f"{n}.")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(55, 65, 81)
        self.set_x(20)
        self.multi_cell(180, 5.5, texto)
        self.set_text_color(0, 0, 0)

    def codigo(self, lineas):
        self.set_fill_color(243, 244, 246)
        self.set_draw_color(209, 213, 219)
        x, y = self.get_x(), self.get_y()
        h = len(lineas) * 5.5 + 6
        self.rect(10, y, 190, h, "FD")
        self.set_font("Courier", "", 8.5)
        self.set_text_color(31, 41, 55)
        self.ln(3)
        for ln in lineas:
            self.set_x(14)
            self.cell(0, 5.5, ln, ln=True)
        self.ln(3)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)

    def tabla(self, cabeceras, filas, anchos=None):
        if anchos is None:
            w = 190 // len(cabeceras)
            anchos = [w] * len(cabeceras)
        self.set_fill_color(37, 99, 235)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 9)
        for i, h in enumerate(cabeceras):
            self.cell(anchos[i], 7, f" {h}", border=1, fill=True)
        self.ln()
        self.set_text_color(0, 0, 0)
        for idx, fila in enumerate(filas):
            self.set_fill_color(249, 250, 251) if idx % 2 == 0 else self.set_fill_color(255, 255, 255)
            self.set_font("Helvetica", "", 9)
            for i, celda in enumerate(fila):
                self.cell(anchos[i], 6, f" {celda}", border=1, fill=True)
            self.ln()
        self.ln(3)

    def badge(self, texto):
        self.set_font("Helvetica", "B", 8.5)
        ancho = self.get_string_width(texto) + 8
        if self.get_x() + ancho > 195:
            self.ln(8)
            self.set_x(10)
        self.set_fill_color(219, 234, 254)
        self.set_text_color(29, 78, 216)
        self.cell(ancho, 6, texto, fill=True, ln=False)
        self.set_x(self.get_x() + 3)
        self.set_text_color(0, 0, 0)

    def arch_tag(self, texto):
        self.set_font("Helvetica", "B", 9)
        ancho = self.get_string_width(texto) + 10
        self.set_fill_color(254, 243, 199)
        self.set_draw_color(217, 119, 6)
        self.set_text_color(146, 64, 14)
        self.cell(ancho, 7, texto, border=1, fill=True, ln=False)
        self.set_x(self.get_x() + 4)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)


# ── helpers de dibujo ──────────────────────────────────────────────────────────

def _box(pdf, x, y, w, h, texto, fill_rgb=(219, 234, 254), text_rgb=(29, 78, 216), bold=False):
    pdf.set_fill_color(*fill_rgb)
    pdf.set_draw_color(37, 99, 235)
    pdf.rect(x, y, w, h, "FD")
    pdf.set_font("Helvetica", "B" if bold else "", 8)
    pdf.set_text_color(*text_rgb)
    pdf.set_xy(x, y + (h - 5) / 2)
    pdf.cell(w, 5, texto, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)


def _db_box(pdf, x, y, w, h, texto):
    _box(pdf, x, y, w, h, texto, fill_rgb=(209, 250, 229), text_rgb=(6, 95, 70))


def _arrow_h(pdf, x1, y, x2):
    pdf.set_draw_color(100, 116, 139)
    pdf.line(x1, y, x2 - 2, y)
    pdf.set_fill_color(100, 116, 139)
    pdf.set_xy(x2 - 3, y - 1.5)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(4, 3, ">")
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)


def _arrow_v(pdf, x, y1, y2):
    pdf.set_draw_color(100, 116, 139)
    pdf.line(x, y1, x, y2 - 2)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(100, 116, 139)
    pdf.set_xy(x - 2, y2 - 3)
    pdf.cell(4, 3, "v")
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)


def _label(pdf, x, y, texto):
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(100, 116, 139)
    pdf.set_xy(x, y)
    pdf.cell(20, 3, texto)
    pdf.set_text_color(0, 0, 0)


# ── diagramas ──────────────────────────────────────────────────────────────────

def diagrama_general(pdf):
    """Diagrama de flujo general del sistema."""
    pdf.subtitulo("Diagrama general del sistema")
    sy = pdf.get_y() + 2

    # Fila 1: Usuario -> Web -> FastAPI -> ChatService
    _box(pdf, 10, sy, 28, 10, "Usuario", fill_rgb=(243, 244, 246), text_rgb=(55, 65, 81))
    _arrow_h(pdf, 38, sy + 5, 48)
    _box(pdf, 48, sy, 32, 10, "Interfaz Web")
    _arrow_h(pdf, 80, sy + 5, 90)
    _box(pdf, 90, sy, 28, 10, "FastAPI")
    _arrow_h(pdf, 118, sy + 5, 128)
    _box(pdf, 128, sy, 32, 10, "ChatService", bold=True)

    # Fila 2: ChatService -> tres columnas (Embeddings, LLM, SQLite)
    cy = sy + 28
    _box(pdf, 92, cy, 32, 10, "Embeddings")
    _box(pdf, 130, cy, 32, 10, "Groq / Gemini")
    _box(pdf, 168, cy, 22, 10, "SQLite", fill_rgb=(254, 243, 199), text_rgb=(146, 64, 14))

    # Fila 3: ChromaDB
    dy = cy + 22
    _db_box(pdf, 92, dy, 32, 10, "ChromaDB")

    # Flechas verticales desde ChatService
    mid_cs = 144
    _arrow_v(pdf, mid_cs - 14, sy + 10, cy)        # -> Embeddings
    _arrow_v(pdf, mid_cs + 2, sy + 10, cy)          # -> LLM
    _arrow_v(pdf, mid_cs + 17, sy + 10, cy)         # -> SQLite

    # Flecha Embeddings -> ChromaDB
    _arrow_v(pdf, 108, cy + 10, dy)

    # Ingesta lateral
    ix = 10
    iy = cy
    _box(pdf, ix, iy, 28, 10, "PDFs /datos", fill_rgb=(243, 244, 246), text_rgb=(55, 65, 81))
    _arrow_v(pdf, ix + 14, iy + 10, dy)
    _db_box(pdf, ix, dy, 28, 10, "ingest.py")
    _arrow_h(pdf, ix + 28, dy + 5, 92)

    pdf.set_y(sy + 65)
    pdf.ln(2)


def diagrama_ingesta(pdf):
    """Pipeline de ingesta offline."""
    pdf.subtitulo("Pipeline de ingesta (offline)")
    sy = pdf.get_y() + 2
    bw, bh, gap = 34, 10, 4
    xs = [10, 10 + bw + gap, 10 + 2*(bw + gap), 10 + 3*(bw + gap), 10 + 4*(bw + gap)]

    labels = ["PDFs /datos", "PyPDFLoader", "TextSplitter", "Embeddings", "ChromaDB"]
    fills  = [
        (243, 244, 246), (219, 234, 254), (219, 234, 254),
        (219, 234, 254), (209, 250, 229),
    ]
    texts  = [
        (55, 65, 81), (29, 78, 216), (29, 78, 216),
        (29, 78, 216), (6, 95, 70),
    ]

    for i, (x, lbl) in enumerate(zip(xs, labels)):
        _box(pdf, x, sy, bw, bh, lbl, fill_rgb=fills[i], text_rgb=texts[i])
        if i < len(labels) - 1:
            _arrow_h(pdf, x + bw, sy + bh/2, x + bw + gap)

    # subtextos
    subs = ["", "extrae texto", "chunk 800\noverlap 100", "text-embedding\n-004", "/db/chroma"]
    for i, (x, sub) in enumerate(zip(xs, subs)):
        if sub:
            lines = sub.split("\n")
            for j, ln in enumerate(lines):
                _label(pdf, x, sy + bh + 2 + j * 4, ln)

    pdf.set_y(sy + 28)
    pdf.ln(2)


def diagrama_capas(pdf):
    """Diagrama de arquitectura en capas."""
    pdf.subtitulo("Arquitectura en capas")
    sy = pdf.get_y() + 2
    lh, lw, gap = 12, 170, 4

    capas = [
        ("Presentacion  (main.py + static/)", (219, 234, 254), (29, 78, 216)),
        ("Servicios  (services/chat_service.py)", (233, 213, 255), (88, 28, 135)),
        ("Infraestructura  (infrastructure/)", (209, 250, 229), (6, 95, 70)),
    ]
    notas = [
        "Endpoints REST, interfaz web. Sin logica de negocio.",
        "Orquesta RAG: busqueda, prompt y log.",
        "ChromaDB, LLM (Groq/Gemini), SQLite.",
    ]

    for i, ((lbl, fill, col), nota) in enumerate(zip(capas, notas)):
        y = sy + i * (lh + gap)
        _box(pdf, 20, y, lw, lh, lbl, fill_rgb=fill, text_rgb=col, bold=True)
        pdf.set_font("Helvetica", "I", 7.5)
        pdf.set_text_color(100, 116, 139)
        pdf.set_xy(20, y + lh + 0.5)
        pdf.cell(lw, 3, nota, align="C")
        pdf.set_text_color(0, 0, 0)
        if i < len(capas) - 1:
            _arrow_v(pdf, 105, y + lh + 3.5, y + lh + gap)

    pdf.set_y(sy + 3 * (lh + gap) + 4)
    pdf.ln(2)


# ── construccion del PDF ───────────────────────────────────────────────────────

pdf = PDF()
pdf.set_margins(10, 10, 10)
pdf.set_auto_page_break(auto=True, margin=15)

pdf.portada()

# 1. DESCRIPCION
pdf.nueva_seccion(1, "Descripcion del Proyecto")
pdf.parrafo(
    "ADE-Bot es un chatbot institucional desarrollado para el area de Ingenieria en Diseno. "
    "Responde consultas sobre el pensum, tramites administrativos, "
    "licitaciones, normativas de diseno, presupuesto y seguridad en obras, utilizando unicamente "
    "informacion de los documentos oficiales del area."
)
pdf.parrafo(
    "El bot esta disponible a traves de una interfaz web moderna con visor de materiales 3D integrado."
)
pdf.subtitulo("Objetivos")
pdf.item("Centralizar el acceso a informacion institucional del area ADE en un solo canal conversacional.")
pdf.item("Reducir la carga de consultas repetitivas al personal administrativo.")
pdf.item("Garantizar precision mayor o igual al 90% en las respuestas mediante un banco de pruebas controlado.")
pdf.item("Facilitar la consulta de materiales y normativas con modelos 3D interactivos.")
pdf.subtitulo("Tecnologias Utilizadas")
pdf.ln(2)
for t in ["Python 3.11+", "FastAPI", "LangChain", "ChromaDB", "Google Gemini",
          "Groq / Llama", "SQLite", "Tailwind CSS", "Sketchfab"]:
    pdf.badge(t)
pdf.ln(10)

# 2. ARQUITECTURA
pdf.nueva_seccion(2, "Arquitectura del Sistema")
pdf.parrafo("El proyecto combina dos patrones complementarios:")
pdf.ln(3)
pdf.arch_tag("RAG")
pdf.arch_tag("Arquitectura en Capas")
pdf.ln(12)

pdf.subtitulo("RAG (Retrieval-Augmented Generation)")
pdf.parrafo(
    "Es el patron principal de inteligencia artificial. Cada consulta pasa por tres etapas "
    "antes de llegar al modelo de lenguaje:"
)
pdf.item_num(1, "Recuperacion: la consulta se convierte en un vector de embeddings y se buscan "
                "los fragmentos de documentos con mayor similitud semantica en ChromaDB.")
pdf.item_num(2, "Aumentacion: los fragmentos recuperados se concatenan como contexto al prompt del sistema.")
pdf.item_num(3, "Generacion: el modelo de lenguaje (Groq o Gemini) genera una respuesta fundamentada "
                "exclusivamente en ese contexto.")
pdf.parrafo(
    "Esto evita que el bot alucine informacion: si no hay fragmentos relevantes, lo indica "
    "y responde desde conocimiento general."
)

pdf.subtitulo("Arquitectura en Capas")
pdf.parrafo("El codigo se organiza en tres capas con responsabilidades claras:")
pdf.tabla(
    ["Capa", "Carpeta", "Responsabilidad"],
    [
        ["Presentacion", "main.py, static/", "Endpoints REST e interfaz web. Sin logica de negocio."],
        ["Servicios", "services/", "Orquesta la busqueda, construye el prompt y coordina el log."],
        ["Infraestructura", "infrastructure/", "Implementaciones concretas: ChromaDB, LLM y SQLite."],
    ],
    anchos=[38, 38, 114]
)
pdf.parrafo(
    "Cada capa depende de interfaces abstractas, no de implementaciones concretas. "
    "Esto permite sustituir cualquier componente sin modificar la logica de negocio."
)

pdf.subtitulo("Pipeline de Ingesta (Offline)")
pdf.parrafo(
    "Los documentos PDF del area se procesan una sola vez para indexarlos en ChromaDB. "
    "No forma parte del servidor en ejecucion:"
)
pdf.codigo([
    "PDF en /datos",
    "  -> PyPDFLoader (extrae texto por pagina)",
    "  -> RecursiveCharacterTextSplitter (chunk=800, overlap=100)",
    "  -> Asignacion de metadata (tema y fuente por nombre de archivo)",
    "  -> GoogleGenerativeAIEmbeddings (text-embedding-004)",
    "  -> ChromaDB en /db/chroma",
])

# 3. DIAGRAMAS
pdf.nueva_seccion(3, "Diagramas")
diagrama_general(pdf)
diagrama_ingesta(pdf)
diagrama_capas(pdf)

# 4. EQUIPO
pdf.nueva_seccion(4, "Equipo y Modulos")
pdf.tabla(
    ["Modulo", "Nombre", "Area de Responsabilidad"],
    [
        ["1", "Luis Millan",      "Base de Conocimientos: inventario y segmentacion de 6 documentos"],
        ["2", "Arnaldo Perdomo",  "IA y PLN: configuracion del LLM y glosario tecnico"],
        ["3", "Yvanna Bravo",     "Interfaz Web: diseno visual de la aplicacion web"],
        ["4", "Keibel Guilarte",  "Pruebas y Control de Calidad: banco de preguntas y criterio 90%"],
        ["5", "Alejandro Duarte", "Infraestructura y Soporte: hosting, logs y despliegue"],
    ],
    anchos=[20, 44, 126]
)
pdf.subtitulo("Cronograma")
pdf.tabla(
    ["Modulo", "Actividad", "Entregable", "Semana"],
    [
        ["1", "Inventario y segmentacion documental",         "6 documentos limpios",          "1"],
        ["2", "Configuracion IA y flujos de intencion",       "Glosario y logica optimizada",  "3"],
        ["3", "Diseno e implementacion de la interfaz web",   "Interfaz web funcional",        "4"],
        ["4", "Pruebas de estres y control de errores",       "Reporte de depuracion >= 90%",  "5"],
        ["5", "Hosting definitivo, difusion y logs",          "Despliegue en produccion",      "7"],
        ["-", "Entrega formal al profesor",                   "Documento definitivo (PDF)", "20/05/2026"],
    ],
    anchos=[18, 72, 62, 38]
)

# 5. ESTRUCTURA
pdf.nueva_seccion(5, "Estructura del Proyecto")
pdf.codigo([
    "ADE-Bot Project/",
    "+-- main.py                   Servidor FastAPI y endpoints REST",
    "+-- services/",
    "|   `-- chat_service.py       Logica RAG: busqueda, prompt, respuesta y log",
    "+-- infrastructure/",
    "|   +-- llm_client.py         Clientes LLM: GeminiLLMClient y GroqLLMClient",
    "|   +-- vector_store.py       ChromaVectorStore con embeddings de Google",
    "|   `-- log_repository.py     Registro de interacciones en SQLite",
    "+-- ingesta/",
    "|   `-- ingest.py             Pipeline offline: PDF a ChromaDB",
    "+-- tests/",
    "|   `-- banco_preguntas.py    Banco de pruebas del Modulo 4",
    "+-- static/",
    "|   `-- index.html            Interfaz web (chat y visor 3D)",
    "+-- datos/                    PDFs fuente (no versionado)",
    "+-- db/                       ChromaDB y SQLite (generados en ejecucion)",
    "+-- docs/                     Documentacion del proyecto",
    "+-- .env                      Variables de entorno (no versionado)",
    "+-- .env.example              Plantilla de configuracion",
    "`-- requirements.txt          Dependencias Python",
])

# 6. INSTALACION
pdf.nueva_seccion(6, "Guia de Instalacion")
pdf.parrafo("Requisitos previos: Python 3.11+, Git, clave GEMINI_API_KEY (obligatoria) y opcionalmente GROQ_API_KEY.")
pdf.ln(2)

pasos = [
    ("Clonar o descargar el repositorio",
     ["git clone <url-del-repositorio>", "cd \"ADE-Bot Project\""]),
    ("Crear el entorno virtual",
     ["python -m venv .venv"]),
    ("Activar el entorno virtual",
     [".venv\\Scripts\\activate          # Windows",
      "# source .venv/bin/activate     # macOS/Linux"]),
    ("Instalar dependencias",
     ["pip install -r requirements.txt"]),
    ("Configurar variables de entorno",
     ["copy .env.example .env",
      "# Abrir .env y pegar las claves API"]),
    ("Indexar los documentos PDF (primera vez)",
     ["# Colocar los PDFs del area en la carpeta datos/",
      "python -m ingesta.ingest"]),
    ("Levantar el servidor",
     ["python main.py",
      "# La interfaz estara disponible en http://localhost:8000"]),
]

for i, (titulo, cmds) in enumerate(pasos, 1):
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 7, f"  Paso {i}: {titulo}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.codigo(cmds)

# 7. API REST
pdf.nueva_seccion(7, "API REST")
pdf.tabla(
    ["Metodo", "Endpoint", "Descripcion"],
    [
        ["GET",    "/",              "Sirve la interfaz web (index.html)"],
        ["POST",   "/api/chat",      "Envia consulta al bot, recibe respuesta JSON"],
        ["GET",    "/api/fuentes",   "Lista PDFs adjuntos a una sesion"],
        ["POST",   "/api/upload",    "Adjunta un PDF a la sesion activa"],
        ["DELETE", "/api/upload",    "Elimina un PDF adjunto de la sesion"],
    ],
    anchos=[22, 46, 122]
)
pdf.subtitulo("Ejemplo: POST /api/chat")
pdf.codigo([
    'curl -X POST http://localhost:8000/api/chat \\',
    '  -H "Content-Type: application/json" \\',
    '  -d \'{"mensaje": "cuantos creditos tiene estructuras", "session_id": "abc123"}\'',
    "",
    "# Respuesta:",
    '{"respuesta": "La materia Estructuras I tiene 4 creditos segun el pensum vigente."}',
])
pdf.parrafo("Los documentos de sesion se almacenan en memoria y se pierden al reiniciar el servidor.")
pdf.parrafo("La API no requiere autenticacion en entorno de desarrollo.")

# 8. INTERFAZ WEB
pdf.nueva_seccion(8, "Interfaz Web")
pdf.parrafo(
    "La interfaz (static/index.html) es una aplicacion web de pagina unica construida con "
    "Tailwind CSS y JavaScript vanilla. No requiere framework adicional."
)
pdf.subtitulo("Componentes principales")
pdf.tabla(
    ["Componente", "Descripcion"],
    [
        ["Panel de chat",     "Conversaciones multiples con historial en la barra lateral izquierda"],
        ["Visor 3D",          "Modelos Sketchfab de 14 materiales de ingenieria, activados automaticamente"],
        ["Subida de PDF",     "Adjunta un documento a la sesion activa para ampliar el contexto del bot"],
        ["Historial",         "Las ultimas sesiones se guardan en localStorage del navegador"],
        ["Materiales activos","Al mencionar un material en la consulta, el visor lo selecciona en la barra"],
    ],
    anchos=[40, 150]
)
pdf.subtitulo("Materiales disponibles en el visor 3D")
pdf.tabla(
    ["Material", "Material", "Material", "Material"],
    [
        ["Acero Inoxidable", "Aluminio",      "Titanio",         "Cobre"],
        ["Fibra de Carbono", "Polimero",      "Ceramica",        "Concreto"],
        ["Madera",           "Vidrio",        "Hormigon",        "Bronce"],
        ["Plastico ABS",     "Acero al Carbon","",""],
    ],
    anchos=[48, 48, 48, 46]
)

# 9. PRUEBAS
pdf.nueva_seccion(9, "Pruebas y Control de Calidad")
pdf.parrafo("Responsable: Keibel Guilarte   |   Criterio de aprobacion: >= 90% de precision")
pdf.subtitulo("Banco de preguntas")
pdf.tabla(
    ["Categoria", "Cantidad", "Descripcion"],
    [
        ["Consultas institucionales", "8",  "El bot debe encontrar contexto y responder"],
        ["Fuera de alcance",          "4",  "El bot debe reconocer que no corresponde al area"],
    ],
    anchos=[60, 24, 106]
)
pdf.subtitulo("Casos de prueba")
pdf.tabla(
    ["Consulta", "Resultado esperado"],
    [
        ["oye cuantos creditos tiene estructuras", "Resolver"],
        ["pa pedir un permiso que hago",           "Resolver"],
        ["que necesito pa inscribir la materia",   "Resolver"],
        ["que vaina necesito pa la licitacion",    "Resolver"],
        ["el blueprint ese como se llama",         "Resolver"],
        ["reglamento de las obras",                "Resolver"],
        ["informacion del area",                   "Resolver"],
        ["cuanto cuesta el tramite",               "Resolver"],
        ["ayudame con mi tesis",                   "Rechazar"],
        ["cual es la capital de venezuela",        "Rechazar"],
        ["como programo en python",                "Rechazar"],
        ["dimelo en ingles",                       "Rechazar"],
    ],
    anchos=[140, 50]
)
pdf.subtitulo("Ejecutar el banco")
pdf.codigo(["python -m tests.banco_preguntas"])
pdf.subtitulo("Como funcionan los dobles de prueba")
pdf.parrafo(
    "El banco usa fakes para los tres componentes del ChatService: _FakeVectorStore, "
    "_FakeLLMClient y _FakeLogRepository. Esto permite correr las pruebas sin conexion "
    "a Gemini ni a ChromaDB, evitando consumo de cuota."
)

# 10. SEGURIDAD
pdf.nueva_seccion(10, "Seguridad")
pdf.tabla(
    ["Aspecto", "Medida implementada"],
    [
        ["Claves API",        "Almacenadas solo en .env, excluido de git via .gitignore"],
        ["Archivos sensibles","datos/ y db/ ignorados por git"],
        ["Entrada del usuario","Texto enviado como JSON, sin ejecucion de comandos"],
        ["Carga de archivos", "Validacion de extension .pdf antes de procesar"],
        ["Sesiones",          "session_id generado aleatoriamente por el frontend"],
    ],
    anchos=[44, 146]
)

# 11. DEPENDENCIAS
pdf.nueva_seccion(11, "Dependencias")
pdf.tabla(
    ["Paquete", "Version minima", "Uso"],
    [
        ["fastapi",                  "0.115.0", "Framework web y definicion de endpoints REST"],
        ["uvicorn",                  "0.30.0",  "Servidor ASGI para FastAPI"],
        ["langchain",                "0.3.0",   "Orquestacion del pipeline RAG"],
        ["langchain-google-genai",   "2.0.0",   "Cliente Gemini (embeddings y LLM)"],
        ["langchain-groq",           "-",        "Cliente Groq (LLM alternativo)"],
        ["langchain-chroma",         "0.1.4",   "Integracion ChromaDB con LangChain"],
        ["chromadb",                 "0.5.23",  "Base de datos vectorial local"],
        ["pypdf",                    "4.2.0",   "Extraccion de texto de archivos PDF"],
        ["python-dotenv",            "1.0.1",   "Carga de variables de entorno desde .env"],
        ["python-multipart",         "0.0.9",   "Soporte para carga de archivos (multipart)"],
        ["langchain-text-splitters", "0.3.0",   "Division de documentos en fragmentos"],
    ],
    anchos=[52, 28, 110]
)

pdf.output("docs/documentacion.pdf")
print("PDF generado: docs/documentacion.pdf")
