"""Recuperación semántica sobre los fragmentos indexados.

La similitud coseno se calcula en Python. Para el corpus de este proyecto
(un reglamento, del orden de cientos de artículos) esto es
instantáneo y evita montar una base vectorial aparte, lo que además
respetaría la restricción C03 si mañana se mueve a PostgreSQL.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from django.conf import settings

from ..models import Chunk
from .ai_provider import embed_query


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve(question: str, top_k: int | None = None) -> list[RetrievedChunk]:
    """Devuelve los fragmentos más parecidos a la pregunta, de mayor a menor."""
    top_k = top_k or settings.RAG_TOP_K

    chunks = list(
        Chunk.objects.filter(document__is_active=True)
        .exclude(embedding=[])
        .select_related("document")
    )

    if not chunks:
        return []

    question_vector = embed_query(question)

    scored = [
        RetrievedChunk(chunk=chunk, score=cosine_similarity(question_vector, chunk.embedding))
        for chunk in chunks
    ]
    scored.sort(key=lambda item: item.score, reverse=True)

    return scored[:top_k]
