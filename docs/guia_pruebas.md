# Guía de Pruebas y Control de Calidad — Módulo 4

Responsable: Keibel Guilarte  
Criterio de aprobación: **≥ 90 % de precisión**

---

## Banco de preguntas

Archivo: `tests/banco_preguntas.py`

El banco contiene 12 casos de prueba que cubren dos categorías:

| Categoría                  | Cantidad | Descripción                                               |
|----------------------------|----------|-----------------------------------------------------------|
| Consultas institucionales  | 8        | El bot **debe** encontrar contexto y responder            |
| Fuera de alcance           | 4        | El bot **debe** reconocer que no corresponde al área      |

### Casos actuales

| Consulta                                    | Resultado esperado |
|---------------------------------------------|--------------------|
| "oye cuantos creditos tiene estructuras"    | Resolver           |
| "pa pedir un permiso que hago"              | Resolver           |
| "que necesito pa inscribir la materia"      | Resolver           |
| "que vaina necesito pa la licitacion"       | Resolver           |
| "el blueprint ese como se llama"            | Resolver           |
| "reglamento de las obras"                   | Resolver           |
| "informacion del area"                      | Resolver           |
| "cuanto cuesta el tramite"                  | Resolver           |
| "ayudame con mi tesis"                      | Rechazar           |
| "cual es la capital de venezuela"           | Rechazar           |
| "como programo en python"                   | Rechazar           |
| "dimelo en ingles"                          | Rechazar           |

---

## Ejecutar el banco

```bash
python -m tests.banco_preguntas
```

**Salida esperada (aprobado):**

```
--- Resultado del banco de pruebas ---
Aprobadas : 12/12
Precision : 100.0%
Criterio  : >= 90%
Estado    : APROBADO
```

---

## Cómo funciona la evaluación

El banco usa **dobles de prueba** (fakes) para los tres componentes del `ChatService`:

- `_FakeVectorStore` — devuelve fragmentos o lista vacía según si la consulta debe resolverse
- `_FakeLLMClient` — devuelve siempre `"respuesta de prueba"` (el contenido no se evalúa)
- `_FakeLogRepository` — registra en memoria cada interacción

La prueba verifica el campo `resuelta` del log: si coincide con el valor esperado, la pregunta se aprueba.

> Esto permite correr el banco **sin conexión a Gemini ni a ChromaDB**, lo que evita consumo de cuota durante las pruebas.

---

## Añadir nuevos casos

Edita la lista `BANCO` en `tests/banco_preguntas.py`:

```python
BANCO = [
    ...
    ("nueva consulta informal sobre el area", True),   # debe resolver
    ("pregunta completamente ajena al area",  False),  # debe rechazar
]
```

Cada tupla es `(texto_consulta, debe_ser_resuelta)`.

---

## Interpretación del resultado

| Precisión  | Estado    | Acción                                                      |
|------------|-----------|-------------------------------------------------------------|
| ≥ 90 %     | APROBADO  | El sistema cumple el criterio de calidad del Módulo 4       |
| < 90 %     | RECHAZADO | Revisar fragmentos indexados, threshold y prompts del sistema |

---

## Criterios adicionales de calidad

Más allá del banco automatizado, se evalúan manualmente:

1. **Tono institucional** — Las respuestas deben ser claras, formales y amables
2. **Citación de fuente** — El bot debe indicar de qué documento proviene la información
3. **Manejo de fuera de alcance** — Respuesta protocolar sin alucinar datos del área
4. **Lenguaje informal** — El bot debe entender jerga estudiantil (ver columna izquierda del banco)
5. **Latencia** — Tiempo de respuesta aceptable bajo uso normal (< 10 s por consulta)
