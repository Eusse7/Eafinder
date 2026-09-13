# Eafinder

Chatbot basado en inteligencia artificial especializado y entrenado con contenidos de la Universidad EAFIT, interfaz web intuitiva y de fácil uso para la centralización de información, capacidad de respuesta a preguntas en lenguaje natural sobre reglamentos, trámites y servicios.

# Comandos

## Requisitos

* Node.js
* pnpm
* Python
* uv

## Instalar uv

### Windows

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Backend

Entrar al backend:

```bash
cd backend
```

Instalar dependencias:

```bash
uv sync
```

Aplicar migraciones:

```bash
uv run python manage.py migrate
```

Levantar el servidor:

```bash
uv run python manage.py runserver
```

Backend:

```text
http://localhost:8000
```

## Frontend

Entrar al frontend:

```bash
cd frontend
```

Instalar dependencias:

```bash
pnpm install
```

Crear el archivo `.env`:

```env
VITE_API_URL=http://localhost:8000
```

Levantar el servidor:

```bash
pnpm dev
```

Frontend:

```text
http://localhost:5173
```

## Desarrollo

### Backend

```bash
cd backend
uv run python manage.py runserver
```

### Frontend

```bash
cd frontend
pnpm run dev
```

Ejecutar cada uno en una terminal diferente.
