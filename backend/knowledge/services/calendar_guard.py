"""Control y filtro de consultas sobre el calendario académico dinámico (US-17).

EAFinder responde preguntas sobre el Reglamento Académico de EAFIT.
Por definición del alcance (US-17):

  1. Las preguntas sobre límites de tiempo o plazos reglamentarios (ej. días
     hábiles para apelar una decisión disciplinaria o calificación, semanas para
     cancelar materias, semestres máximos) se responden exclusivamente con base
     en los artículos del Reglamento Académico, citando el artículo exacto y
     advirtiendo que el sistema no gestiona fechas específicas de calendario.
  2. Si el usuario pregunta por fechas dinámicas del calendario académico
     (p. ej. cuándo inician clases en un año específico, semanas de receso, fechas
     límite de pago del semestre o fechas de ceremonias de grado), el sistema
     responde aclarando que solo maneja normas reglamentarias y no el calendario
     académico, remitiendo a los canales oficiales (Autoservicio EPIK o web EAFIT).

Este módulo provee la detección local de consultas dirigidas a fechas dinámicas
del calendario académico para responder de manera determinista, sin consumo de tokens
y evitando alucinaciones de fechas cambiantes.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class CalendarCheckResult:
    """Resultado de la verificación de consulta sobre calendario dinámico."""

    is_calendar_query: bool
    message: str = ""


CALENDAR_OUT_OF_SCOPE_MESSAGE = (
    "Solo gestiono normas, trámites y plazos del Reglamento Académico de EAFIT, "
    "no las fechas dinámicas del calendario académico (como fecha de inicio o "
    "fin de clases, semanas de receso, fechas límite de pago o exámenes).\n\n"
    "Para consultar las fechas específicas del calendario académico vigente, por "
    "favor revisa el Cronograma de Actividades oficial en la página web de EAFIT "
    "o ingresa a Autoservicio EPIK."
)

_PATTERNS: list[re.Pattern[str]] = [
    # Inicio o fin de clases / periodos
    re.compile(
        r"\b("
        r"cuando (inician|empiezan|comienzan|terminan|acaban|finalizan) (las )?clases|"
        r"fecha(s)? de (inicio|comienzo|finalizacion|terminacion|fin) de clases|"
        r"cuando (inicia|empieza|comienza|termina|acaba|finaliza) el (semestre|periodo)|"
        r"when do classes (start|begin|end)|(start|end) of classes"
        r")\b"
    ),
    # Semanas de receso / vacaciones / semana santa
    re.compile(
        r"\b("
        r"cuando es (la|el) (semana de receso|receso|vacaciones|semana santa)|"
        r"fechas? de (vacaciones|receso|semana santa)|"
        r"when is (the )?(recess|break|vacation)"
        r")\b"
    ),
    # Fechas límite de pago
    re.compile(
        r"\b("
        r"(fecha(s)? limite(s)?|hasta cuando puedo|plazo limite) (de pago|para pagar|pagar) (de |en )?(la )?(matricula|el semestre)|"
        r"fecha(s)? (limite(s)? )?de pago|"
        r"cuando se paga la matricula|"
        r"tuition payment deadline|when is tuition due"
        r")\b"
    ),
    # Consulta explícita por calendario académico o cronograma
    re.compile(
        r"\b("
        r"calendario academico|cronograma de actividades|fechas del calendario|"
        r"academic calendar"
        r")\b"
    ),
    # Fechas de ceremonias de grado en calendario
    re.compile(
        r"\b("
        r"fecha(s)? de (la )?(ceremonia de grado|los grados)|"
        r"cuando son los grados (de|en) 20\d\d|"
        r"graduation ceremony date"
        r")\b"
    ),
]


def _normalize(text: str) -> str:
    """Minúsculas, sin tildes y con espacios colapsados."""
    lowered = text.casefold()
    decomposed = unicodedata.normalize("NFKD", lowered)
    without_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", without_accents).strip()


def check_calendar_query(text: str) -> CalendarCheckResult:
    """Detecta si la consulta pregunta por fechas dinámicas del calendario académico."""
    normalized = _normalize(text)
    for pattern in _PATTERNS:
        if pattern.search(normalized):
            return CalendarCheckResult(
                is_calendar_query=True,
                message=CALENDAR_OUT_OF_SCOPE_MESSAGE,
            )
    return CalendarCheckResult(is_calendar_query=False)


__all__ = ["CALENDAR_OUT_OF_SCOPE_MESSAGE", "CalendarCheckResult", "check_calendar_query"]
