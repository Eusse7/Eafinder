"""Adaptador del proveedor de IA externo.

El SRS (1.1-d) pide que el proveedor se consuma a través de un adaptador,
de modo que cambiarlo no se propague al resto del sistema. Todo el
proyecto habla con estas dos funciones: `embed_texts` y `generate_answer`.

Proveedores soportados (se elige con AI_PROVIDER en el .env):

    gemini  -> Google AI Studio   (capa gratuita, no pide tarjeta)
    openai  -> OpenAI             (requiere saldo)

Si no hay API key configurada se lanza `AIProviderError`, y la vista de
chat lo traduce a un mensaje comprensible para el usuario (US11).
"""

from __future__ import annotations

import time

import httpx
from django.conf import settings

TIMEOUT = httpx.Timeout(60.0, connect=10.0)

# El tier gratuito limita las peticiones por minuto. Un 429 casi nunca
# significa "se acabó la cuota": significa "vas muy rápido". Se reintenta
# con espera creciente en vez de abortar la indexación completa.
MAX_REINTENTOS = 6
ESPERA_BASE = 5  # segundos


class AIProviderError(RuntimeError):
    """El proveedor externo no respondió o no está configurado."""


def _api_key() -> str:
    key = settings.AI_API_KEY
    if not key:
        raise AIProviderError(
            "No hay AI_API_KEY configurada. Copia backend/.env.example a "
            "backend/.env y agrega tu clave del proveedor de IA."
        )
    return key


def _espera(response: httpx.Response | None, intento: int) -> float:
    """Cuánto esperar antes de reintentar.

    Se respeta la cabecera Retry-After si el proveedor la manda; si no,
    espera creciente: 5s, 10s, 20s, 40s...
    """
    if response is not None:
        cabecera = response.headers.get("Retry-After")
        if cabecera:
            try:
                return min(float(cabecera), 120.0)
            except ValueError:
                pass

    return min(ESPERA_BASE * (2**intento), 120.0)


def _mensaje_de_error(codigo: int, detalle: str) -> str:
    detalle = detalle[:600]

    if codigo == 429:
        pista = (
            "\n\nEs el límite de peticiones por minuto del proveedor, no la "
            f"cuota total. Ya se reintentó {MAX_REINTENTOS} veces con esperas "
            "crecientes.\n"
            "Qué hacer:\n"
            "  1. Espera unos minutos y vuelve a correr el comando. La "
            "indexación es atómica: no quedó nada a medias.\n"
            "  2. Si persiste, baja AI_EMBED_BATCH_SIZE en backend/.env "
            "(por ejemplo a 5).\n"
            "  3. Revisa tu consumo real en https://ai.dev/rate-limit"
        )
    elif codigo in (403, 404):
        pista = (
            "\n\nCausas habituales:\n"
            "  1. El modelo configurado fue retirado por el proveedor.\n"
            "  2. La clave tiene restricciones, o pertenece a un proyecto "
            "sin la API habilitada.\n"
            "Consulta qué modelos acepta tu clave en:\n"
            "  https://generativelanguage.googleapis.com/v1beta/models?key=TU_CLAVE"
        )
    else:
        pista = ""

    return f"El proveedor de IA respondió {codigo}: {detalle}{pista}"


def _post(url: str, *, json: dict, headers: dict | None = None) -> dict:
    """POST con reintentos ante 429 y errores temporales del servidor."""
    for intento in range(MAX_REINTENTOS):
        es_ultimo = intento == MAX_REINTENTOS - 1

        try:
            response = httpx.post(url, json=json, headers=headers or {}, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as error:
            codigo = error.response.status_code
            recuperable = codigo == 429 or 500 <= codigo < 600

            if not recuperable or es_ultimo:
                raise AIProviderError(
                    _mensaje_de_error(codigo, error.response.text)
                ) from error

            time.sleep(_espera(error.response, intento))

        except httpx.HTTPError as error:
            if es_ultimo:
                raise AIProviderError(
                    f"No se pudo contactar al proveedor de IA: {error}"
                ) from error

            time.sleep(_espera(None, intento))

    raise AIProviderError("No se pudo contactar al proveedor de IA.")


# --------------------------------------------------------------------------
# Embeddings
# --------------------------------------------------------------------------


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Convierte una lista de textos en una lista de vectores."""
    if not texts:
        return []

    if settings.AI_PROVIDER == "openai":
        return _embed_openai(texts)
    return _embed_gemini(texts)


def _embed_gemini(texts: list[str]) -> list[list[float]]:
    model = settings.AI_EMBEDDING_MODEL
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:batchEmbedContents?key={_api_key()}"
    )
    payload = {
        "requests": [
            {
                "model": f"models/{model}",
                "content": {"parts": [{"text": text}]},
            }
            for text in texts
        ]
    }
    data = _post(url, json=payload)
    return [item["values"] for item in data.get("embeddings", [])]


def _embed_openai(texts: list[str]) -> list[list[float]]:
    data = _post(
        "https://api.openai.com/v1/embeddings",
        json={"model": settings.AI_EMBEDDING_MODEL, "input": texts},
        headers={"Authorization": f"Bearer {_api_key()}"},
    )
    return [item["embedding"] for item in data["data"]]


def embed_query(text: str) -> list[float]:
    """Embedding de una sola pregunta."""
    vectors = embed_texts([text])
    if not vectors:
        raise AIProviderError("El proveedor no devolvió un embedding para la pregunta.")
    return vectors[0]


# --------------------------------------------------------------------------
# Generación
# --------------------------------------------------------------------------


def generate_answer(system_prompt: str, user_prompt: str) -> str:
    """Genera la respuesta final en lenguaje natural."""
    if settings.AI_PROVIDER == "openai":
        return _generate_openai(system_prompt, user_prompt)
    return _generate_gemini(system_prompt, user_prompt)


def _config_de_generacion(model: str) -> dict:
    """Parámetros de generación.

    Ojo con los modelos Gemini 3.x: razonan antes de responder y esos
    "pensamientos" se descuentan de maxOutputTokens. Con un tope bajo la
    respuesta puede llegar vacía. Por eso el tope es holgado y el nivel de
    razonamiento se deja bajo.
    """
    config: dict = {
        "temperature": 0.2,
        "maxOutputTokens": settings.AI_MAX_OUTPUT_TOKENS,
    }

    if settings.AI_THINKING_LEVEL and model.startswith("gemini-3"):
        config["thinkingLevel"] = settings.AI_THINKING_LEVEL

    return config


def _texto_de_respuesta(data: dict) -> str:
    """Saca el texto de la respuesta de Gemini, explicando si viene vacía."""
    candidatos = data.get("candidates") or []

    if not candidatos:
        raise AIProviderError(
            "El proveedor no devolvió ninguna respuesta. Puede ser un filtro "
            "de seguridad sobre la pregunta."
        )

    candidato = candidatos[0]
    partes = (candidato.get("content") or {}).get("parts") or []
    texto = "".join(parte.get("text", "") for parte in partes).strip()

    if texto:
        return texto

    motivo = candidato.get("finishReason", "desconocido")

    if motivo == "MAX_TOKENS":
        raise AIProviderError(
            "La respuesta se truncó antes de empezar: el razonamiento del "
            "modelo consumió todo el presupuesto de tokens.\n"
            "Sube AI_MAX_OUTPUT_TOKENS en backend/.env (por ejemplo a 4096), "
            "o baja AI_THINKING_LEVEL a 'minimal'."
        )

    raise AIProviderError(
        f"El proveedor devolvió una respuesta vacía (finishReason: {motivo})."
    )


def _generate_gemini(system_prompt: str, user_prompt: str) -> str:
    model = settings.AI_CHAT_MODEL
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={_api_key()}"
    )
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": _config_de_generacion(model),
    }

    try:
        data = _post(url, json=payload)
    except AIProviderError as error:
        # Si el modelo no conoce thinkingLevel, se reintenta sin ese campo
        # en vez de obligar a tocar la configuración a mano.
        if "thinkingLevel" in payload["generationConfig"] and "400" in str(error):
            payload["generationConfig"].pop("thinkingLevel")
            data = _post(url, json=payload)
        else:
            raise

    return _texto_de_respuesta(data)


def _generate_openai(system_prompt: str, user_prompt: str) -> str:
    data = _post(
        "https://api.openai.com/v1/chat/completions",
        json={
            "model": settings.AI_CHAT_MODEL,
            "temperature": 0.2,
            "max_tokens": settings.AI_MAX_OUTPUT_TOKENS,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        headers={"Authorization": f"Bearer {_api_key()}"},
    )
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as error:
        raise AIProviderError("El proveedor devolvió una respuesta vacía.") from error
