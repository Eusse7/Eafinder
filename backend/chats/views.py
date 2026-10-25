import logging

from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from knowledge.services.ai_provider import AIProviderError
from knowledge.services.rag import answer_question

from .models import Chat, Message, MessageSource

logger = logging.getLogger(__name__)

MAX_CHATS_PER_SESSION = 5
HISTORY_MESSAGES = 6
TITLE_MAX_LENGTH = 60


def serialize_source(source: MessageSource) -> dict:
    return {
        "id": str(source.id),
        "label": source.label,
        "document_title": source.document_title,
        "article_ref": source.article_ref,
        "excerpt": source.excerpt,
    }


def serialize_message(message: Message) -> dict:
    return {
        "id": str(message.id),
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at,
        "feedback": message.feedback,
        "moderated": message.moderated,
        "sources": [serialize_source(source) for source in message.sources.all()],
    }


def build_title(text: str) -> str:
    """Título del chat a partir de la primera pregunta."""
    clean = " ".join(text.split())
    if len(clean) <= TITLE_MAX_LENGTH:
        return clean
    return clean[: TITLE_MAX_LENGTH - 1].rstrip() + "…"


@api_view(["POST"])
def create_chat(request):
    session_id = request.data.get("session_id")

    if not session_id:
        return Response({"error": "El session_id es obligatorio."}, status=400)

    active_chats = Chat.objects.filter(session_id=session_id).count()

    if active_chats >= MAX_CHATS_PER_SESSION:
        return Response(
            {"error": f"Has alcanzado el límite de {MAX_CHATS_PER_SESSION} chats."},
            status=400,
        )

    chat = Chat.objects.create(session_id=session_id)

    return Response({"id": str(chat.id), "title": chat.title})


@api_view(["GET"])
def get_chats(request):
    session_id = request.query_params.get("session_id")

    if not session_id:
        return Response({"error": "El session_id es obligatorio."}, status=400)

    chats = Chat.objects.filter(session_id=session_id).order_by("-created_at")

    return Response(
        [
            {
                "id": str(chat.id),
                "title": chat.title,
                "created_at": chat.created_at,
            }
            for chat in chats
        ]
    )


@api_view(["POST"])
def create_message(request, chat_id):
    """Registra la pregunta y genera la respuesta anclada (US01, US04, US08)."""
    content = request.data.get("content", "").strip()

    if not content:
        return Response({"error": "El contenido es obligatorio."}, status=400)

    chat = get_object_or_404(Chat, id=chat_id)

    is_first_message = not chat.messages.exists()

    user_message = Message.objects.create(
        chat=chat,
        role=Message.Role.USER,
        content=content,
    )

    if is_first_message:
        chat.title = build_title(content)
        chat.save(update_fields=["title"])

    history = [
        {"role": message.role, "content": message.content}
        for message in chat.messages.exclude(id=user_message.id).order_by("-created_at")[
            :HISTORY_MESSAGES
        ][::-1]
    ]

    try:
        answer = answer_question(content, history)
    except AIProviderError as error:
        # US11: el error se reporta en términos comprensibles y la pregunta
        # del usuario no se pierde. El detalle real queda en la consola del
        # servidor, porque el mensaje del chat no puede mostrarlo todo.
        logger.error("Fallo del proveedor de IA: %s", error)
        assistant_message = Message.objects.create(
            chat=chat,
            role=Message.Role.ASSISTANT,
            content=(
                "No pude comunicarme con el servicio de inteligencia artificial. "
                "Vuelve a intentarlo en unos segundos."
            ),
        )
        return Response(
            {
                "user_message": serialize_message(user_message),
                "assistant_message": serialize_message(assistant_message),
                "chat_title": chat.title,
                "error": str(error) if settings.DEBUG else None,
            },
            status=200,
        )

    assistant_message = Message.objects.create(
        chat=chat,
        role=Message.Role.ASSISTANT,
        content=answer.content,
        moderated=answer.moderated,
    )

    MessageSource.objects.bulk_create(
        [
            MessageSource(
                message=assistant_message,
                chunk=item.chunk,
                document_title=item.chunk.document.title,
                article_ref=item.chunk.article_ref,
                excerpt=item.chunk.content[:1200],
                relevance=item.score,
            )
            for item in answer.sources
        ]
    )

    assistant_message.refresh_from_db()

    return Response(
        {
            "user_message": serialize_message(user_message),
            "assistant_message": serialize_message(assistant_message),
            "chat_title": chat.title,
        }
    )


@api_view(["PATCH"])
def set_feedback(request, chat_id, message_id):
    """Registra el pulgar arriba/abajo de una respuesta del asistente (US15).

    Acepta "up", "down" o "" (para quitar la valoración). Solo se puede
    valorar un mensaje del asistente.
    """
    valor = request.data.get("feedback", "")

    opciones_validas = {choice.value for choice in Message.Feedback} | {""}
    if valor not in opciones_validas:
        return Response(
            {"error": "El feedback debe ser 'up', 'down' o vacío."},
            status=400,
        )

    message = get_object_or_404(Message, id=message_id, chat_id=chat_id)

    if message.role != Message.Role.ASSISTANT:
        return Response(
            {"error": "Solo se pueden valorar las respuestas del asistente."},
            status=400,
        )

    message.feedback = valor
    message.save(update_fields=["feedback"])

    return Response(serialize_message(message))


@api_view(["GET", "DELETE"])
def get_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if request.method == "DELETE":
        chat.delete()
        return Response(status=204)

    limit = 10
    before = request.query_params.get("before")

    messages_query = Message.objects.filter(chat=chat).prefetch_related("sources")

    if before:
        cursor_message = get_object_or_404(Message, id=before, chat=chat)

        messages_query = messages_query.filter(
            Q(created_at__lt=cursor_message.created_at)
            | Q(created_at=cursor_message.created_at, id__lt=cursor_message.id)
        )

    messages = list(messages_query.order_by("-created_at", "-id")[: limit + 1])

    has_more = len(messages) > limit

    messages = messages[:limit]
    messages.reverse()

    next_cursor = str(messages[0].id) if has_more and messages else None

    return Response(
        {
            "id": str(chat.id),
            "title": chat.title,
            "created_at": chat.created_at,
            "messages": [serialize_message(message) for message in messages],
            "has_more": has_more,
            "next_cursor": next_cursor,
        }
    )


@api_view(["GET"])
def chat_exists(request, chat_id):
    return Response({"exists": Chat.objects.filter(id=chat_id).exists()})


@api_view(["GET"])
def health(request):
    """Estado del backend y de la base de conocimiento.

    El frontend lo usa para el indicador de conexión y para avisar cuando
    todavía no hay documentos indexados.
    """
    from knowledge.models import Chunk, Document

    return Response(
        {
            "status": "ok",
            "documents": Document.objects.filter(is_active=True).count(),
            "chunks": Chunk.objects.filter(document__is_active=True).count(),
            "ai_provider": settings.AI_PROVIDER,
            "ai_configured": bool(settings.AI_API_KEY),
        }
    )


# --------------------------------------------------------------------------
# Panel de analítica de búsquedas (US05)
# --------------------------------------------------------------------------

TOPIC_KEYWORDS = {
    "Matrícula e inscripción": ["matricul", "inscri", "admitid", "registro"],
    "Cancelación de asignaturas": ["cancel", "retir"],
    "Prueba académica y promedio": ["prueba", "promedio", "3.0", "sancion"],
    "Requisitos y trámite de grado": ["grado", "gradua", "titulo", "diploma"],
    "Homologación y convalidación": ["homolog", "validac", "convalid", "credito"],
    "Calificaciones y reclamo de notas": ["nota", "calificac", "reclamo", "revision"],
    "Exámenes y evaluaciones": ["examen", "parcial", "supletorio", "evaluac", "asistenc"],
}


def _normalize_text(text: str) -> str:
    """Minúsculas y sin tildes para búsqueda de palabras clave."""
    import re
    import unicodedata

    lowered = text.casefold()
    decomposed = unicodedata.normalize("NFKD", lowered)
    without_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", without_accents).strip()


def get_analytics_data() -> dict:
    """Calcula las métricas agregadas de consultas para US05 y US18."""
    from django.db.models import Count
    from django.db.models.functions import TruncDate
    from knowledge.services.gap_tracker import get_gap_report

    user_messages = Message.objects.filter(role=Message.Role.USER)
    total_queries = user_messages.count()
    total_chats = Chat.objects.count()
    gap_data = get_gap_report()

    if total_queries == 0:
        return {
            "has_data": False,
            "total_queries": 0,
            "total_chats": total_chats,
            "satisfaction_rate": None,
            "feedback_up": 0,
            "feedback_down": 0,
            "moderated_queries": 0,
            "frequent_topics": [],
            "daily_volume": [],
            "knowledge_gaps": gap_data,
        }

    # Temas frecuentes analizando el contenido de las preguntas
    topic_counts = {name: 0 for name in TOPIC_KEYWORDS}
    otros_count = 0

    for msg in user_messages.values_list("content", flat=True):
        normalized = _normalize_text(msg)
        matched = False
        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(kw in normalized for kw in keywords):
                topic_counts[topic] += 1
                matched = True
        if not matched:
            otros_count += 1

    frequent_topics = []
    for topic, count in topic_counts.items():
        if count > 0:
            percentage = round((count / total_queries) * 100, 1)
            frequent_topics.append({"topic": topic, "count": count, "percentage": percentage})

    if otros_count > 0:
        frequent_topics.append({
            "topic": "Otras consultas normativas",
            "count": otros_count,
            "percentage": round((otros_count / total_queries) * 100, 1),
        })

    frequent_topics.sort(key=lambda item: item["count"], reverse=True)

    # Métricas de satisfacción (US15)
    feedback_up = Message.objects.filter(feedback=Message.Feedback.UP).count()
    feedback_down = Message.objects.filter(feedback=Message.Feedback.DOWN).count()
    total_feedback = feedback_up + feedback_down
    satisfaction_rate = (
        round((feedback_up / total_feedback) * 100, 1) if total_feedback > 0 else None
    )

    moderated_queries = Message.objects.filter(moderated=True).count()

    # Volumen diario (últimos 14 días con actividad)
    daily_rows = (
        user_messages.annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("-day")[:14]
    )
    daily_volume = [
        {"date": row["day"].isoformat(), "count": row["count"]}
        for row in reversed(list(daily_rows))
    ]

    return {
        "has_data": True,
        "total_queries": total_queries,
        "total_chats": total_chats,
        "satisfaction_rate": satisfaction_rate,
        "feedback_up": feedback_up,
        "feedback_down": feedback_down,
        "moderated_queries": moderated_queries,
        "frequent_topics": frequent_topics,
        "daily_volume": daily_volume,
        "knowledge_gaps": gap_data,
    }


@api_view(["GET"])
def analytics(request):
    """Devuelve las métricas agregadas del panel de analítica de búsquedas (US05) y brechas (US18)."""
    return Response(get_analytics_data())


@api_view(["GET"])
def knowledge_gaps_report(request):
    """Reporte de brechas de conocimiento y consultas sin respuesta (US18)."""
    from knowledge.services.gap_tracker import get_gap_report

    return Response(get_gap_report())
