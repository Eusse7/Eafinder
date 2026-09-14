import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { ApiService } from './api.service';
import { ChatSummary, Health, Message } from './models';

export const MAX_CHATS = 5;

/**
 * Estado compartido de la aplicación.
 *
 * Se usa un servicio con signals en vez de una librería de estado: para el
 * tamaño de este proyecto alcanza y no agrega dependencias.
 */
@Injectable({ providedIn: 'root' })
export class ChatStore {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);

  readonly chats = signal<ChatSummary[]>([]);
  readonly messages = signal<Message[]>([]);
  readonly activeChatId = signal<string | null>(null);

  readonly loadingChats = signal(false);
  readonly loadingMessages = signal(false);
  /** US07: indicador mientras el asistente genera la respuesta. */
  readonly sending = signal(false);
  readonly backendOnline = signal(true);
  readonly health = signal<Health | null>(null);
  readonly toast = signal<string | null>(null);

  readonly knowledgeBaseEmpty = computed(() => {
    const health = this.health();
    return health !== null && health.chunks === 0;
  });

  // -------------------------------------------------------------------
  // Estado del backend (US11)
  // -------------------------------------------------------------------

  async checkHealth(): Promise<void> {
    try {
      const health = await firstValueFrom(this.api.health());
      this.health.set(health);
      this.backendOnline.set(true);
    } catch {
      this.backendOnline.set(false);
    }
  }

  // -------------------------------------------------------------------
  // Conversaciones
  // -------------------------------------------------------------------

  async loadChats(): Promise<void> {
    this.loadingChats.set(true);

    try {
      this.chats.set(await firstValueFrom(this.api.listChats()));
      this.backendOnline.set(true);
    } catch {
      this.backendOnline.set(false);
    } finally {
      this.loadingChats.set(false);
    }
  }

  async loadChat(chatId: string): Promise<boolean> {
    this.loadingMessages.set(true);
    this.activeChatId.set(chatId);

    try {
      const chat = await firstValueFrom(this.api.getChat(chatId));
      this.messages.set(chat.messages);
      return true;
    } catch {
      this.messages.set([]);
      return false;
    } finally {
      this.loadingMessages.set(false);
    }
  }

  async deleteChat(chatId: string): Promise<void> {
    await firstValueFrom(this.api.deleteChat(chatId));
    await this.loadChats();

    if (this.activeChatId() === chatId) {
      this.activeChatId.set(null);
      this.messages.set([]);
      await this.router.navigate(['/']);
    }
  }

  // -------------------------------------------------------------------
  // Envío de preguntas (US01, US04, US08)
  // -------------------------------------------------------------------

  /**
   * Envía una pregunta. Si no hay conversación activa crea una primero, de
   * modo que el usuario puede escribir directamente desde la pantalla
   * inicial sin pensar en "crear un chat".
   */
  async ask(content: string): Promise<void> {
    const text = content.trim();

    if (!text || this.sending()) {
      return;
    }

    let chatId = this.activeChatId();

    if (!chatId) {
      try {
        const chat = await firstValueFrom(this.api.createChat());
        chatId = chat.id;
      } catch (error: unknown) {
        this.showToast(
          this.isChatLimit(error)
            ? `Solo puedes tener un máximo de ${MAX_CHATS} chats a la vez.`
            : 'No se pudo crear la conversación. Revisa tu conexión.',
        );
        return;
      }

      this.activeChatId.set(chatId);
      this.messages.set([]);
      await this.router.navigate(['/chat', chatId]);
    }

    this.sending.set(true);

    // La pregunta se muestra de inmediato; la respuesta llega después.
    const optimistic: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
      sources: [],
    };
    this.messages.update((messages) => [...messages, optimistic]);

    try {
      const response = await firstValueFrom(this.api.sendMessage(chatId, text));

      this.messages.update((messages) => [
        ...messages.filter((message) => message.id !== optimistic.id),
        response.user_message,
        response.assistant_message,
      ]);

      await this.loadChats();
    } catch {
      this.messages.update((messages) =>
        messages.filter((message) => message.id !== optimistic.id),
      );
      this.showToast(
        'No se pudo enviar tu consulta. Revisa tu conexión e inténtalo de nuevo.',
      );
      this.backendOnline.set(false);
    } finally {
      this.sending.set(false);
    }
  }

  startNewChat(): void {
    this.activeChatId.set(null);
    this.messages.set([]);
    this.router.navigate(['/']);
  }

  showToast(message: string): void {
    this.toast.set(message);
    setTimeout(() => this.toast.set(null), 4000);
  }

  private isChatLimit(error: unknown): boolean {
    return (
      typeof error === 'object' &&
      error !== null &&
      'status' in error &&
      (error as { status: number }).status === 400
    );
  }
}
