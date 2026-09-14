"""Extracción de texto y división en fragmentos.

La división se hace por artículo cuando el documento los tiene (que es el
caso del Reglamento Académico), porque eso es lo que permite citar
"Artículo 42" en la respuesta (US09). Si no se detectan artículos, se cae
a una división por tamaño.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# "ARTÍCULO 42", "Articulo 42.", "Art. 42" -- con o sin tilde, en cualquier caja.
ARTICLE_PATTERN = re.compile(
    r"^\s*(art[íi]culo|art\.)\s*(\d+[a-zA-Z]?)\s*[.\-:]?",
    re.IGNORECASE | re.MULTILINE,
)

MAX_CHARS = 1500
OVERLAP = 150


@dataclass
class RawChunk:
    position: int
    article_ref: str
    content: str


def extract_text(path: Path) -> str:
    """Lee un .pdf, .docx, .txt o .md y devuelve su texto plano."""
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(path)
    if suffix == ".docx":
        return _extract_docx(path)
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")

    raise ValueError(f"Formato no soportado: {suffix}. Usa .pdf, .docx, .txt o .md")


def _extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as error:  # pragma: no cover
        raise ImportError("Falta la dependencia pypdf. Corre: uv sync") from error

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages)

    if not text.strip():
        raise ValueError(
            "El PDF no tiene texto extraíble (probablemente es un escaneo). "
            "Usa una versión con texto seleccionable."
        )
    return text


def _extract_docx(path: Path) -> str:
    try:
        import docx
    except ImportError as error:  # pragma: no cover
        raise ImportError("Falta la dependencia python-docx. Corre: uv sync") from error

    document = docx.Document(str(path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def clean(text: str) -> str:
    """Normaliza espacios y quita saltos de línea sobrantes."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split(text: str) -> list[RawChunk]:
    """Divide el texto en fragmentos, preferiblemente uno por artículo."""
    text = clean(text)
    matches = list(ARTICLE_PATTERN.finditer(text))

    if len(matches) < 2:
        return _split_by_size(text)

    chunks: list[RawChunk] = []
    for position, match in enumerate(matches):
        start = match.start()
        end = matches[position + 1].start() if position + 1 < len(matches) else len(text)
        body = text[start:end].strip()

        if not body:
            continue

        chunks.append(
            RawChunk(
                position=position,
                article_ref=f"Artículo {match.group(2)}",
                content=body[: MAX_CHARS * 2],
            )
        )

    return chunks


def _split_by_size(text: str) -> list[RawChunk]:
    chunks: list[RawChunk] = []
    start = 0
    position = 0

    while start < len(text):
        end = min(start + MAX_CHARS, len(text))
        body = text[start:end].strip()

        if body:
            chunks.append(RawChunk(position=position, article_ref="", content=body))
            position += 1

        if end == len(text):
            break
        start = end - OVERLAP

    return chunks
