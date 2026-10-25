"""Servicio de registro y análisis de brechas de conocimiento (US18).

Permite registrar automáticamente las preguntas sin respuesta y generar alertas
para que el equipo del proyecto identifique qué documentos normativos hacen falta.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from django.db.models import Avg, Count, Max, Min

from knowledge.models import KnowledgeGap


def _normalize_query(query: str) -> str:
    """Normaliza texto para agrupar consultas con intenciones similares."""
    lowered = query.casefold()
    decomposed = unicodedata.normalize("NFKD", lowered)
    without_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    cleaned = re.sub(r"[^\w\s]", "", without_accents)
    return re.sub(r"\s+", " ", cleaned).strip()


def record_gap(
    query: str,
    reason: str = KnowledgeGap.Reason.LOW_RELEVANCE,
    max_similarity: float = 0.0,
) -> KnowledgeGap:
    """Registra una consulta que no pudo ser respondida por el pipeline RAG (Escenario 1).

    Guarda únicamente el texto de la pregunta y metadatos del intento, respetando
    la privacidad al no almacenar datos del usuario ni identificadores personales.
    """
    clean_query = query.strip()
    norm = _normalize_query(clean_query)[:255]

    return KnowledgeGap.objects.create(
        query=clean_query,
        normalized_query=norm,
        reason=reason,
        max_similarity=round(max_similarity, 3),
    )


def get_gap_report(min_count: int = 1) -> dict[str, Any]:
    """Genera el reporte de brechas de conocimiento recurrentes (Escenario 2)."""
    total_gaps = KnowledgeGap.objects.count()
    pending_gaps = KnowledgeGap.objects.filter(status=KnowledgeGap.Status.PENDING).count()

    if total_gaps == 0:
        return {
            "has_gaps": False,
            "total_gaps": 0,
            "pending_gaps": 0,
            "has_alerts": False,
            "recurring_gaps": [],
        }

    grouped = (
        KnowledgeGap.objects.filter(status=KnowledgeGap.Status.PENDING)
        .values("normalized_query")
        .annotate(
            count=Count("id"),
            sample_query=Min("query"),
            last_asked=Max("created_at"),
            avg_similarity=Avg("max_similarity"),
        )
        .filter(count__gte=min_count)
        .order_by("-count", "-last_asked")[:20]
    )

    recurring_list = []
    has_alerts = False

    for item in grouped:
        count = item["count"]
        if count >= 2:
            has_alerts = True
        recurring_list.append(
            {
                "query": item["sample_query"],
                "normalized_query": item["normalized_query"],
                "count": count,
                "last_asked": item["last_asked"].isoformat() if item["last_asked"] else "",
                "avg_similarity": round(item["avg_similarity"] or 0.0, 3),
                "is_recurring": count >= 2,
            }
        )

    return {
        "has_gaps": total_gaps > 0,
        "total_gaps": total_gaps,
        "pending_gaps": pending_gaps,
        "has_alerts": has_alerts or pending_gaps >= 3,
        "recurring_gaps": recurring_list,
    }
