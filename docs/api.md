# Referencia de la API REST — ADE-Bot

Base URL: `http://localhost:8000`

---

## GET `/`

Sirve la interfaz web.

**Respuesta:** `text/html` — `static/index.html`

---

## POST `/api/chat`

Envía una consulta al bot y recibe una respuesta.

**Cuerpo (JSON):**

```json
{
  "mensaje": "¿Cuántos créditos tiene la materia Estructuras?",
  "session_id": "abc123"
}
```

| Campo        | Tipo   | Obligatorio | Descripción                                              |
|--------------|--------|-------------|----------------------------------------------------------|
| `mensaje`    | string | sí          | Texto de la consulta del usuario                         |
| `session_id` | string | no          | Identificador de sesión. Default: `"anonimo"`            |

**Respuesta (200):**

```json
{
  "respuesta": "La materia Estructuras I tiene 4 créditos según el pensum vigente..."
}
```

**Flujo interno:**

1. Busca fragmentos similares en ChromaDB (top_k=4, threshold=0.75)
2. Si hay documentos adjuntos a la sesión, los incluye como contexto adicional
3. Construye el prompt con el sistema de Juanito el Inge
4. Llama a Gemini y devuelve la respuesta
5. Registra la interacción en SQLite

---

## GET `/api/fuentes`

Lista los archivos PDF adjuntos a una sesión activa.

**Query params:**

| Parámetro    | Tipo   | Default     |
|--------------|--------|-------------|
| `session_id` | string | `"anonimo"` |

**Ejemplo:** `GET /api/fuentes?session_id=abc123`

**Respuesta (200):**

```json
{
  "archivos": ["contrato_2024.pdf", "pensum_diseno.pdf"]
}
```

---

## POST `/api/upload`

Adjunta un archivo PDF a una sesión. El texto extraído se usa como contexto extra en las consultas de esa sesión.

**Cuerpo (multipart/form-data):**

| Campo        | Tipo   | Obligatorio | Descripción                            |
|--------------|--------|-------------|----------------------------------------|
| `archivo`    | file   | sí          | Archivo PDF a adjuntar                 |
| `session_id` | string | no          | Identificador de sesión. Default: `"anonimo"` |

**Respuesta (200):**

```json
{
  "archivo": "contrato_2024.pdf",
  "paginas": 12
}
```

**Errores:**

| Código | Mensaje                              | Causa                           |
|--------|--------------------------------------|---------------------------------|
| 400    | `"Solo se aceptan archivos PDF."`    | El archivo no es `.pdf`         |
| 422    | `"No se pudo extraer texto del PDF."` | PDF sin texto extraíble (imagen) |

---

## DELETE `/api/upload`

Elimina un archivo adjunto de una sesión.

**Query params:**

| Parámetro    | Tipo   | Obligatorio |
|--------------|--------|-------------|
| `session_id` | string | sí          |
| `filename`   | string | sí          |

**Ejemplo:** `DELETE /api/upload?session_id=abc123&filename=contrato_2024.pdf`

**Respuesta (200):**

```json
{ "ok": true }
```

---

## Notas

- Los documentos de sesión se almacenan **en memoria**; se pierden al reiniciar el servidor.
- El `session_id` es generado aleatoriamente por el frontend (`Math.random().toString(36)`).
- La API no requiere autenticación en el entorno de desarrollo.
