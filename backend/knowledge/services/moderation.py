"""Filtro de moderación de contenido sensible (US20).

Se ejecuta ANTES del pipeline RAG: si la pregunta del estudiante contiene
contenido sensible, el sistema no la envía al modelo de IA ni busca en el
reglamento. En su lugar responde de forma segura y, cuando corresponde,
remite a un canal de ayuda institucional.

El objetivo no es censurar preguntas legítimas sobre el reglamento, sino:

  1. No procesar odio, acoso o insultos dirigidos.
  2. Responder con empatía y derivar a ayuda ante señales de autolesión.
  3. Rechazar peticiones claramente fuera del propósito académico y de
     contenido explícito.

La detección es local, por palabras clave en español: no depende del
proveedor externo, así que funciona incluso sin conexión y sin costo, y
el filtro nunca deja pasar contenido sensible por un fallo de red. Es un
primer filtro deliberadamente conservador; el prompt del sistema (regla 1
y 2 de rag.py) sigue siendo la segunda línea de defensa.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum


class Category(str, Enum):
    SELF_HARM = "self_harm"
    HATE = "hate"
    SEXUAL = "sexual"
    VIOLENCE = "violence"


@dataclass(frozen=True)
class ModerationResult:
    """Resultado del filtro. `flagged=False` significa vía libre al RAG."""

    flagged: bool
    category: Category | None = None
    message: str = ""


# --------------------------------------------------------------------------
# Mensajes de respuesta segura por categoría
# --------------------------------------------------------------------------

_SELF_HARM_MESSAGE = (
    "Lamento que estés pasando por un momento difícil. No estás solo y tu "
    "bienestar importa.\n\n"
    "Si sientes que puedes hacerte daño, por favor busca ayuda ahora mismo:\n"
    "  • Línea de la Vida (Colombia): 106\n"
    "  • En EAFIT, Desarrollo Humano ofrece acompañamiento psicológico "
    "gratuito a los estudiantes.\n\n"
    "Soy un asistente sobre el reglamento académico y no puedo brindar "
    "apoyo profesional, pero las personas de esas líneas sí pueden ayudarte."
)

_HATE_MESSAGE = (
    "No puedo ayudar con mensajes que incluyan insultos, discriminación o "
    "ataques a personas o grupos.\n\n"
    "Si tienes una consulta sobre el Reglamento Académico de EAFIT, "
    "reformúlala y con gusto te ayudo."
)

_SEXUAL_MESSAGE = (
    "Soy el asistente del Reglamento Académico de EAFIT y no puedo responder "
    "contenido de tipo sexual o explícito.\n\n"
    "¿Tienes alguna consulta sobre trámites o normas académicas?"
)

_VIOLENCE_MESSAGE = (
    "No puedo ayudar con peticiones relacionadas con violencia o actividades "
    "que puedan causar daño.\n\n"
    "Si tu consulta es sobre el Reglamento Académico de EAFIT, con gusto "
    "te ayudo."
)

_MESSAGES: dict[Category, str] = {
    Category.SELF_HARM: _SELF_HARM_MESSAGE,
    Category.HATE: _HATE_MESSAGE,
    Category.SEXUAL: _SEXUAL_MESSAGE,
    Category.VIOLENCE: _VIOLENCE_MESSAGE,
}


# --------------------------------------------------------------------------
# Patrones por categoría
# --------------------------------------------------------------------------
# Se buscan como palabra completa (\b ... \b) sobre el texto normalizado
# (sin tildes y en minúsculas), para no marcar coincidencias dentro de
# palabras legítimas (p. ej. "matar" no debe saltar por "rematar").

_PATTERNS: list[tuple[Category, re.Pattern[str]]] = [
    (
        Category.SELF_HARM,
        re.compile(
            r"\b("
            r"suicid\w*|quitarme la vida|matarme|me quiero morir|"
            r"no quiero (seguir )?vivir|hacerme dano|autolesion\w*|"
            r"cortarme|acabar con mi vida"
            r")\b"
        ),
    ),
    (
        Category.HATE,
        re.compile(
            r"\b("
            r"estupid\w*|idiot\w*|imbecil\w*|maric\w*|negro de mierda|"
            r"odio a (los|las)|no sirves|eres un\w* (inutil|basura)|"
            r"malparid\w*|hijueputa|gonorrea"
            r")\b"
        ),
    ),
    (
        Category.SEXUAL,
        re.compile(
            r"\b("
            r"porno\w*|contenido sexual|desnud\w*|sexo explicito|"
            r"nudes|xxx"
            r")\b"
        ),
    ),
    (
        Category.VIOLENCE,
        re.compile(
            r"\b("
            r"como (hacer|fabricar|construir) (una )?(bomba|explosivo\w*|arma\w*)|"
            r"matar a|asesinar|como atacar a|hacer dano a (alguien|otr\w*)"
            r")\b"
        ),
    ),
]


def _normalize(text: str) -> str:
    """Minúsculas, sin tildes y con espacios colapsados."""
    lowered = text.casefold()
    decomposed = unicodedata.normalize("NFKD", lowered)
    without_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", without_accents).strip()


def moderate(text: str) -> ModerationResult:
    """Clasifica el texto. Devuelve `flagged=True` si es contenido sensible.

    El orden importa: autolesión se evalúa primero porque su respuesta es
    de cuidado y nunca debe quedar enmascarada por otra categoría.
    """
    normalized = _normalize(text)

    for category, pattern in _PATTERNS:
        if pattern.search(normalized):
            return ModerationResult(
                flagged=True,
                category=category,
                message=_MESSAGES[category],
            )

    return ModerationResult(flagged=False)


__all__ = ["Category", "ModerationResult", "moderate"]
