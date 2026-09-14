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
