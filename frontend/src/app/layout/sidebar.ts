import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

import { ChatStore } from '../core/chat.store';
import { ChatSummary } from '../core/models';

@Component({
  selector: 'app-sidebar',
  imports: [RouterLink, RouterLinkActive],
  template: `
    @if (open) {
      <div class="sidebar-overlay" (click)="closed.emit()"></div>
    }

    <aside class="sidebar" [class.sidebar-open]="open">
      <div class="sidebar-inner">
        <div class="sidebar-header">
          <span class="brand-mark">EAFIT</span>
          <span class="brand-name">EAFinder</span>

          <button type="button" class="icon-button sidebar-close" (click)="closed.emit()">
            ✕
          </button>
        </div>

        <button type="button" class="new-chat" (click)="onNewChat()">
          + Nueva conversación
        </button>

        <div class="chat-list">
          <h2 class="chat-list-title">Recientes</h2>

          @if (store.loadingChats()) {
            <p class="muted">Cargando…</p>
          } @else if (!store.backendOnline()) {
            <p class="error">No se pudo conectar al backend</p>
          } @else if (store.chats().length === 0) {
            <p class="muted">Aún no tienes conversaciones.</p>
          } @else {
            @for (chat of store.chats(); track chat.id) {
              <div class="chat-item" routerLinkActive="chat-item-active">
                <a [routerLink]="['/chat', chat.id]" class="chat-item-link" (click)="onOpenChat()">
                  {{ chat.title }}
                </a>

                <button
                  type="button"
                  class="icon-button chat-delete"
                  (click)="askDelete(chat)"
                  aria-label="Eliminar conversación"
                >
                  ✕
                </button>
              </div>
            }
          }
        </div>

        <div class="sidebar-footer">
          <p>Universidad EAFIT · {{ year }}</p>
          <p class="muted small">Respuestas informativas. La interpretación oficial
            corresponde a la instancia competente.</p>
        </div>
      </div>
    </aside>

    @if (chatToDelete) {
      <div class="modal-backdrop" (click)="chatToDelete = null">
        <div class="modal" (click)="$event.stopPropagation()">
          <h3>Eliminar conversación</h3>
          <p>¿Seguro que quieres eliminar «{{ chatToDelete.title }}»? Esta acción no se puede deshacer.</p>

          <div class="modal-actions">
            <button type="button" class="button-ghost" (click)="chatToDelete = null">
              Cancelar
            </button>
            <button type="button" class="button-danger" [disabled]="deleting" (click)="confirmDelete()">
              {{ deleting ? 'Eliminando…' : 'Eliminar' }}
            </button>
          </div>
        </div>
      </div>
    }
  `,
})
export class Sidebar {
  @Input() open = true;
  @Output() closed = new EventEmitter<void>();

  protected readonly store = inject(ChatStore);
  protected readonly year = new Date().getFullYear();

  protected chatToDelete: ChatSummary | null = null;
  protected deleting = false;

  /** En móvil la barra lateral se cierra al navegar; en escritorio se queda. */
  onOpenChat(): void {
    if (window.innerWidth < 640) {
      this.closed.emit();
    }
  }

  onNewChat(): void {
    this.store.startNewChat();
    this.onOpenChat();
  }

  askDelete(chat: ChatSummary): void {
    this.chatToDelete = chat;
  }

  async confirmDelete(): Promise<void> {
    if (!this.chatToDelete) {
      return;
    }

    this.deleting = true;

    try {
      await this.store.deleteChat(this.chatToDelete.id);
      this.chatToDelete = null;
    } finally {
      this.deleting = false;
    }
  }
}
