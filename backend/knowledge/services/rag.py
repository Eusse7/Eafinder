"""Pipeline de respuesta anclada (US01, US04, US08, US09, US10).

El orden de los pasos es el que fija el SRS (1.4-f):

    recuperación -> umbral de relevancia -> generación anclada -> citación

Si ningún fragmento supera el umbral, el sistema NO responde: declara su
limitación y remite al canal oficial. Ese es el control de alucinación
que pide US10.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from django.conf import settings

from .ai_provider import AIProviderError, generate_answer
from .retriever import RetrievedChunk, retrieve

SYSTEM_PROMPT = """\
Eres EAFinder, el asistente de la Universidad EAFIT. Respondes preguntas \
sobre los reglamentos y trámites académicos de la Universidad.

Reglas que no puedes romper:

1. Responde ÚNICAMENTE con información que aparezca en el CONTEXTO. \
Si el contexto no lo dice, no lo digas.
2. Si el contexto no alcanza para responder, dilo explícitamente y sugiere \
consultar a Admisiones y Registro. No inventes ni completes con \
conocimiento general.
3. Cita siempre el artículo del que sacaste la información, con el formato \
(Artículo N).
4. Responde en español, en tono neutral, claro y breve. Usa pasos numerados \
cuando expliques un trámite.
5. No des fechas del calendario académico, tarifas ni valores de matrícula: \
esos datos no están en el reglamento. Remite al canal oficial.
6. Tus respuestas son informativas; la interpretación oficial corresponde a \
la instancia competente de la Universidad.
"""

NO_CONTEXT_MESSAGE = (
    "No encontré información suficiente sobre ese tema en los documentos "
    "institucionales que tengo indexados.\n\n"
    "Te recomiendo consultarlo directamente con Admisiones y Registro o en "
    "la Línea de Servicio de la Universidad EAFIT."
)

EMPTY_KNOWLEDGE_BASE_MESSAGE = (
    "Todavía no tengo documentos indexados, así que no puedo responder "
    "consultas sobre el reglamento.\n\n"
    "Un administrador debe cargar el documento con el comando "
    "`manage.py ingest_document`."
)


@dataclass
class Answer:
    content: str
    sources: list[RetrievedChunk] = field(default_factory=list)
    grounded: bool = False


def build_context(retrieved: list[RetrievedChunk]) -> str:
    bloques = []
    for item in retrieved:
        encabezado = item.chunk.citation
        bloques.append(f"[{encabezado}]\n{item.chunk.content}")
    return "\n\n---\n\n".join(bloques)


def build_user_prompt(question: str, context: str, history: list[dict]) -> str:
    partes = []

    if history:
        conversacion = "\n".join(
            f"{'Estudiante' if item['role'] == 'user' else 'EAFinder'}: {item['content']}"
            for item in history
        )
        partes.append(f"CONVERSACIÓN PREVIA (para resolver preguntas de seguimiento):\n{conversacion}")

    partes.append(f"CONTEXTO:\n{context}")
    partes.append(f"PREGUNTA DEL ESTUDIANTE:\n{question}")

    return "\n\n".join(partes)


def answer_question(question: str, history: list[dict] | None = None) -> Answer:
    """Responde una pregunta usando solo los documentos indexados."""
    history = history or []

    retrieved = retrieve(question)

    if not retrieved:
        return Answer(content=EMPTY_KNOWLEDGE_BASE_MESSAGE, grounded=False)

    relevantes = [item for item in retrieved if item.score >= settings.RAG_MIN_RELEVANCE]

    if not relevantes:
        return Answer(content=NO_CONTEXT_MESSAGE, grounded=False)

    context = build_context(relevantes)
    prompt = build_user_prompt(question, context, history)

    content = generate_answer(SYSTEM_PROMPT, prompt)

    return Answer(content=content, sources=relevantes, grounded=True)


__all__ = ["Answer", "answer_question", "AIProviderError"]
