# EAFinder

Asistente conversacional de la Universidad EAFIT. Responde preguntas en
lenguaje natural sobre el **Reglamento Académico de los programas de
pregrado**, citando siempre el artículo del que sacó la información.

EAFinder solo responde con lo que está en los documentos indexados. Si la
pregunta no está cubierta, lo dice y remite al canal oficial en lugar de
inventar una respuesta.

## Arquitectura

| Capa | Tecnología | Carpeta |
|---|---|---|
| Frontend | Angular (restricción C01) | `frontend/` |
| Backend y pipeline de IA | Django + Django REST Framework (C02) | `backend/` |
| Base de datos | SQLite en desarrollo, relacional (C03) | `backend/db.sqlite3` |
| Embeddings y generación | Proveedor externo vía adaptador | `backend/knowledge/services/` |

El flujo de una pregunta es siempre el mismo:

```
pregunta -> recuperación semántica -> umbral de relevancia
         -> generación anclada al contexto -> citación del artículo
```

Si ningún fragmento supera el umbral de relevancia, el pipeline se detiene
antes de llamar al modelo y devuelve el mensaje de limitación. Ese es el
control de alucinación del sistema.

## Requisitos

* **Python 3.12 o superior** (lo exige Django 6.1)
* **Node.js** 20.19+, 22.12+ o 24+ (lo exige Angular 21)

Verifica lo que tienes instalado:

```bash
python --version
node --version
```

Si te falta Python: <https://www.python.org/downloads/>
(en Windows, marca **"Add python.exe to PATH"** durante la instalación).

Si te falta Node: <https://nodejs.org/>

## Puesta en marcha

### 1. Backend

Todo el backend vive dentro de un **entorno virtual**, para que las
dependencias del proyecto no se mezclen con las de tu sistema ni con las de
otros proyectos.

**Windows (PowerShell)**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

**macOS / Linux**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Cuando el entorno está activo, el prompt muestra `(.venv)` adelante. Si
abres una terminal nueva tienes que volver a activarlo antes de correr
cualquier comando de `manage.py`. Para salir: `deactivate`.

Abre `backend/.env` y pon tu clave del proveedor de IA en `AI_API_KEY`.
Con `AI_PROVIDER=gemini` la clave se saca gratis en
<https://aistudio.google.com/apikey>. También funciona `AI_PROVIDER=openai`.

> `backend/.env` y `backend/.venv/` están en el `.gitignore`.
> **Nunca subas la clave al repositorio.**

```bash
python manage.py migrate
python manage.py runserver
```

Backend en <http://localhost:8000>

### 2. Indexar el reglamento

Sin documentos indexados, EAFinder avisa que no puede responder. Deja el PDF
en `docs/` y córrelo una vez:

```bash
cd backend
python manage.py ingest_document ../docs/reglamento.pdf \
  --title "Reglamento Académico de los programas de pregrado" \
  --doc-version 2025-1
```

El comando extrae el texto, lo parte por artículo, calcula los embeddings y
confirma cuántos fragmentos quedaron indexados.

Para publicar una versión nueva sin perder la anterior:

```bash
python manage.py ingest_document ../docs/reglamento_2026.pdf \
  --title "Reglamento Académico de los programas de pregrado" \
  --doc-version 2026-1 --retire-previous
```

También se puede re-indexar desde el admin de Django
(<http://localhost:8000/admin>, requiere `createsuperuser`).

### 3. Frontend

```bash
cd frontend
npm install
npm start
```

Frontend en <http://localhost:4200>

Si el backend corre en otro puerto, cámbialo en
`frontend/src/environments/environment.ts`.

## Pruebas

```bash
cd backend
python manage.py test
```

Las pruebas no llaman al proveedor externo: los embeddings y la generación
se sustituyen por dobles de prueba, así que corren sin clave y sin costo.

## Historias de usuario cubiertas

| ID | Historia | Dónde |
|---|---|---|
| US01 | Consulta de reglamentos en lenguaje natural | `knowledge/services/rag.py`, `chats/views.py` |
| US02 | Entrenamiento y actualización de la base de conocimiento | `knowledge/management/commands/ingest_document.py`, `knowledge/admin.py` |
| US03 | Acceso mediante interfaz centralizada | `frontend/src/app/pages/welcome/` |
| US04 | Consulta de trámites del Reglamento Académico | prompt del sistema en `rag.py` |
| US08 | Procesamiento de consultas en lenguaje natural | `knowledge/services/retriever.py` |
| US09 | Citación de fuentes institucionales | modelo `MessageSource`, chips de fuente en el chat |
| US10 | Control de alucinación | umbral `RAG_MIN_RELEVANCE` en `rag.py` |

## Estructura

```text
Eafinder/
├── backend/
│   ├── chats/          # conversaciones, mensajes y fuentes citadas
│   ├── knowledge/      # documentos, fragmentos, RAG e ingesta
│   │   ├── services/   # ai_provider · chunker · retriever · indexer · rag
│   │   └── management/commands/ingest_document.py
│   └── config/         # settings, urls, cors
├── frontend/           # aplicación Angular
│   └── src/app/
│       ├── core/       # servicios de API, sesión y estado
│       ├── layout/     # barra lateral, barra superior, campo de consulta
│       └── pages/      # pantalla inicial y conversación
└── docs/               # reglamento a indexar (no se versiona)
```
