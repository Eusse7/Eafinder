from django.contrib import admin, messages

from .models import Chunk, Document
from .services import indexer
from .services.ai_provider import AIProviderError


class ChunkInline(admin.TabularInline):
    model = Chunk
    extra = 0
    fields = ("position", "article_ref", "content")
    readonly_fields = ("position", "article_ref", "content")
    can_delete = False
    max_num = 0


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "version", "is_active", "chunk_count", "indexed_at")
    list_filter = ("is_active",)
    search_fields = ("title",)
    readonly_fields = ("created_at", "indexed_at")
    inlines = [ChunkInline]
    actions = ["reindex_documents", "retire_documents", "activate_documents"]

    @admin.action(description="Re-indexar (recalcular embeddings)")
    def reindex_documents(self, request, queryset):
        for document in queryset:
            try:
                total = indexer.reindex(document)
            except (AIProviderError, ValueError) as error:
                self.message_user(
                    request, f"{document}: {error}", level=messages.ERROR
                )
            else:
                self.message_user(
                    request,
                    f"{document}: {total} fragmentos re-indexados correctamente.",
                    level=messages.SUCCESS,
                )

    @admin.action(description="Retirar (dejar de usar al responder)")
    def retire_documents(self, request, queryset):
        total = queryset.update(is_active=False)
        self.message_user(request, f"{total} documento(s) retirado(s).")

    @admin.action(description="Activar")
    def activate_documents(self, request, queryset):
        total = queryset.update(is_active=True)
        self.message_user(request, f"{total} documento(s) activado(s).")


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ("article_ref", "document", "position")
    list_filter = ("document",)
    search_fields = ("article_ref", "content")
