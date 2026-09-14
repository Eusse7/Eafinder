"""Indexación de documentos: texto -> fragmentos -> embeddings (US02, US12)."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from ..models import Chunk, Document
from . import chunker
from .ai_provider import embed_texts

# Pausa entre lotes para no chocar con el límite por minuto del tier
# gratuito. El adaptador reintenta ante un 429, pero es mejor no provocarlo.
PAUSA_ENTRE_LOTES = 1.0

Progreso = Callable[[int, int], None]


def _embeber_en_lotes(chunks: list[Chunk], on_progress: Progreso | None = None) -> None:
    """Calcula y guarda los embeddings de una lista de fragmentos."""
    tamano = settings.AI_EMBED_BATCH_SIZE
    total = len(chunks)

    for inicio in range(0, total, tamano):
        lote = chunks[inicio : inicio + tamano]

        vectores = embed_texts([chunk.content for chunk in lote])

        for chunk, vector in zip(lote, vectores):
            chunk.embedding = vector

        Chunk.objects.bulk_update(lote, ["embedding"])

        if on_progress:
            on_progress(min(inicio + tamano, total), total)

        if inicio + tamano < total:
            time.sleep(PAUSA_ENTRE_LOTES)


def index_document(
    document: Document,
    text: str,
    on_progress: Progreso | None = None,
) -> int:
    """Reemplaza los fragmentos de un documento y calcula sus embeddings.

    Devuelve la cantidad de fragmentos indexados. Si algo falla a mitad de
    camino, la excepción sube y el documento queda sin fragmentos nuevos,
    de modo que conviene llamar a esta función dentro de una transacción.
    """
    raw_chunks = chunker.split(text)

    if not raw_chunks:
        raise ValueError("No se obtuvo ningún fragmento del documento.")

    document.chunks.all().delete()

    creados = [
        Chunk(
            document=document,
            position=raw.position,
            article_ref=raw.article_ref,
            content=raw.content,
        )
        for raw in raw_chunks
    ]

    Chunk.objects.bulk_create(creados)

    _embeber_en_lotes(creados, on_progress)

    document.indexed_at = timezone.now()
    document.save(update_fields=["indexed_at"])

    return len(creados)


def index_from_file(
    document: Document,
    path: Path,
    on_progress: Progreso | None = None,
) -> int:
    """Extrae el texto de un archivo y lo indexa."""
    text = chunker.extract_text(path)
    return index_document(document, text, on_progress)


def reindex(document: Document, on_progress: Progreso | None = None) -> int:
    """Recalcula los embeddings de los fragmentos ya guardados.

    Útil cuando se cambia de modelo de embeddings y no se quiere volver a
    procesar el archivo original.
    """
    chunks = list(document.chunks.all())

    if not chunks:
        raise ValueError("El documento no tiene fragmentos. Vuelve a ingerir el archivo.")

    _embeber_en_lotes(chunks, on_progress)

    document.indexed_at = timezone.now()
    document.save(update_fields=["indexed_at"])

    return len(chunks)
