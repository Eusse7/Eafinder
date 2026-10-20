import uuid

from django.db import models


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, default="Nueva conversación")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    class Feedback(models.TextChoices):
        """Valoración del usuario sobre una respuesta del asistente (US15)."""

        UP = "up", "Útil"
        DOWN = "down", "No útil"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # US15: pulgar arriba/abajo. Vacío = el usuario aún no valoró la respuesta.
    # Solo tiene sentido en mensajes del asistente.
    feedback = models.CharField(
        max_length=4,
        choices=Feedback.choices,
        blank=True,
        default="",
    )
    # US20: True cuando la respuesta la generó el filtro de moderación de
    # contenido sensible, no el pipeline RAG.
    moderated = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.role}: {self.content[:50]}"


class MessageSource(models.Model):
    """Fragmento citado por una respuesta del asistente (US09).

    Se guarda el texto de la cita y no solo la llave foránea, para que la
    trazabilidad sobreviva aunque el documento se re-indexe o se retire
    (SRS 1.4-e).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name="sources",
    )
    chunk = models.ForeignKey(
        "knowledge.Chunk",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="citations",
    )
    document_title = models.CharField(max_length=200)
    article_ref = models.CharField(max_length=120, blank=True)
    excerpt = models.TextField(
        help_text="Texto literal del artículo citado, para mostrarlo al usuario."
    )
    relevance = models.FloatField(default=0.0)

    class Meta:
        ordering = ["-relevance"]

    def __str__(self) -> str:
        return self.label

    @property
    def label(self) -> str:
        if self.article_ref:
            return f"{self.document_title}, {self.article_ref}"
        return self.document_title
