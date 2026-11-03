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
| Base de datos | SQLite en desarrollo; PostgreSQL en Docker/AWS (C03) | `backend/` |
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
>
> Si usas Docker Compose, configura `AI_API_KEY` en el `.env` de la raíz del
> repositorio (no en `backend/.env`); Compose pasa esa clave al contenedor.

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

También se pueden cargar e indexar nuevos documentos o re-indexar los
existentes directamente desde la interfaz web del admin de Django
(<http://localhost:8000/admin>, requiere `createsuperuser`), usando el botón
**«📤 Cargar e indexar documento»** (US12).

### 3. Frontend

```bash
cd frontend
npm install
npm start
```

Frontend en <http://localhost:4200>

Si el backend corre en otro puerto, cámbialo en
`frontend/src/environments/environment.ts`.

## Docker

Requiere Docker Desktop con Docker Compose. Desde la raíz del proyecto:

```powershell
docker compose up --build
```

La aplicación queda en <http://localhost:8080> y el admin en
<http://localhost:8080/admin/>. Compose inicia PostgreSQL y conserva sus
datos en un volumen. Cambia `AI_API_KEY` en `.env` para habilitar respuestas
de IA (copia `.env.example` a `.env` en la raíz y agrega tu clave). Después de
editar variables, recrea el backend con
`docker compose up -d --force-recreate backend`. Los valores por defecto son
solo para desarrollo local. Para detener los servicios sin borrar datos:
`docker compose down`.

### Acceso de administración y carga de documentos

Crea `.env` desde `.env.example` y define `DJANGO_SUPERUSER_USERNAME`,
`DJANGO_SUPERUSER_EMAIL` y `DJANGO_SUPERUSER_PASSWORD`. Al iniciar el backend,
Compose crea ese administrador o sincroniza su correo y contraseña con esos
valores. Cambia la contraseña en `.env` y reinicia el backend para actualizarla.
El enlace **Administrar documentos** del pie de la interfaz abre el centro
propio de EAFinder en `/gestion/documentos/`, con una pantalla de acceso
personalizada y un panel de carga. El inicio de sesión sigue siendo obligatorio
y solo acepta la cuenta administradora configurada. Desde allí puedes subir
`.pdf`, `.docx`, `.txt` o `.md` y retirar la versión anterior al publicar una
nueva; no es necesario usar Django Admin para esta tarea. La pantalla de
acceso está en `/gestion/ingresar/`.
La indexación puede tardar varios minutos si el archivo contiene muchos
artículos o el proveedor de IA está limitado; deja la pestaña abierta y no
envíes el mismo documento de nuevo mientras procesa.

Para desarrollo local, `DJANGO_CSRF_TRUSTED_ORIGINS` debe incluir
`http://localhost:8080,http://127.0.0.1:8080`; Compose usa esos valores de
forma predeterminada. En AWS, reemplázalos por el origen HTTPS de tu dominio.

El archivo `.env` está excluido de Git; no uses las credenciales de ejemplo
en un servidor público ni compartas ese archivo.

## Despliegue en AWS EC2

La configuración incluye Docker Compose y un perfil de Caddy que termina
HTTPS automáticamente. No crea recursos AWS por sí sola. Antes de empezar,
necesitas una cuenta AWS, un dominio cuyo DNS puedas editar y una instancia
EC2; el costo depende de la región, el tipo de instancia, el almacenamiento,
la IPv4 pública y el tráfico. Revisa AWS Pricing Calculator antes de lanzar
la instancia.

1. En la consola de EC2, lanza Ubuntu Server 24.04 LTS. Para empezar con bajo
   costo, usa la región `us-east-1` y una instancia de al menos 2 GiB de RAM,
   con 20 GB de almacenamiento gp3. Revisa el costo total en AWS Pricing
   Calculator antes de lanzarla. Restringe SSH (puerto 22) a tu IP y permite
   HTTP/HTTPS (80/443); no abras PostgreSQL ni el puerto 8080.
2. Conecta por SSH, instala Docker Engine y el plugin Docker Compose siguiendo
   la guía oficial de Docker para Ubuntu, y clona este repositorio:

   ```bash
   git clone https://github.com/Eusse7/Eafinder.git
   cd Eafinder
   cp .env.example .env
   ```

3. Edita `.env`: establece `DJANGO_DEBUG=False`, un `DJANGO_SECRET_KEY`
   aleatorio (por ejemplo, `openssl rand -base64 48`), una contraseña fuerte
   para `POSTGRES_PASSWORD`, las credenciales iniciales en
   `DJANGO_SUPERUSER_USERNAME` y `DJANGO_SUPERUSER_PASSWORD`, la clave de
   `AI_API_KEY`, y el dominio real en `DOMAIN`, `DJANGO_ALLOWED_HOSTS` y
   `DJANGO_CSRF_TRUSTED_ORIGINS`.
4. Crea un registro DNS tipo A para el dominio apuntando a la IPv4 pública de
   EC2. Si detienes e inicias la instancia, esa IP puede cambiar; para una IP
   estable puedes asociar una Elastic IP (verifica su costo). Asegúrate de
   que los puertos 80 y 443 sean accesibles desde Internet.
5. Desde la raíz del repositorio, construye e inicia la aplicación:

   ```bash
   COMPOSE_PARALLEL_LIMIT=1 docker compose --profile production build
   docker compose --profile production up -d
   ```

   Caddy obtiene y renueva el certificado TLS. La aplicación queda en
   `https://tu-dominio/`; el panel admin, en `https://tu-dominio/admin/`.
   Carga e indexa el reglamento desde el admin o con el comando
   `ingest_document`. La base de conocimiento no viene incluida en el repo.

   Para revisar el estado: `docker compose ps` y
   `docker compose logs -f backend`. Los datos sobreviven a reinicios gracias
   al volumen `postgres_data`; configura copias de seguridad periódicas antes
   de usar el sistema con datos importantes.

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
| US05 | Panel de analítica de búsquedas | `chats/views.py`, `chats/admin.py`, `frontend/src/app/pages/analytics/` |
| US06 | Interfaz de chat responsiva para móvil, tableta y escritorio | `frontend/src/styles.css`, componentes de `layout/` y páginas |
| US07 | Indicador de estado de procesamiento | `frontend/src/app/core/chat.store.ts`, `frontend/src/app/pages/chat/chat.page.html`, `styles.css` |
| US08 | Procesamiento de consultas en lenguaje natural | `knowledge/services/retriever.py` |
| US09 | Citación de fuentes institucionales | modelo `MessageSource`, chips de fuente en el chat |
| US10 | Control de alucinación y respuestas fuera de dominio | umbral `RAG_MIN_RELEVANCE` en `rag.py` |
| US11 | Manejo de errores de conexión | `chats/views.py`, `knowledge/services/ai_provider.py`, `frontend/src/app/core/chat.store.ts` |
| US12 | Carga de nuevos reglamentos | centro propio en `knowledge/views.py` (`/gestion/documentos/`), comando CLI `ingest_document.py` |
| US13 | Actualización o eliminación de documentos obsoletos | opción `--retire-previous` en `ingest_document.py`, acciones en `knowledge/admin.py` |
| US14 | Entrada de voz para consultas | `frontend/src/app/layout/composer.ts`, `frontend/src/styles.css` (Web Speech API) |
| US15 | Valoración de la precisión de las respuestas | modelo `Message.feedback`, endpoint `set_feedback`, botones en `chat.page.html` |
| US16 | Sugerencias de preguntas frecuentes | tarjetas interactivas en `frontend/src/app/pages/welcome/` |
| US17 | Integración con el calendario académico y plazos reglamentarios | `knowledge/services/rag.py`, `knowledge/services/calendar_guard.py` |
| US18 | Registro de consultas sin respuesta y alertas de brechas de conocimiento | modelo `KnowledgeGap`, `gap_tracker.py`, `knowledge/admin.py`, reporte en `/admin/chats/analytics/` |
| US19 | Cambio entre tema claro y oscuro | `frontend/src/app/core/theme.service.ts`, `topbar.ts`, `sidebar.ts`, `styles.css` (persistencia local y preferencia del SO) |
| US20 | Filtro de seguridad y moderación de contenido sensible | `knowledge/services/moderation.py`, `rag.py`, `chats/models.py`, aviso en `chat.page.html` |

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
