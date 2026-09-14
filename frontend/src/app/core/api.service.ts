import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import {
  Chat,
  ChatSummary,
  Health,
  SendMessageResponse,
} from './models';
import { SessionService } from './session.service';

/** Única puerta de salida hacia el backend de Django. */
@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly session = inject(SessionService);
  private readonly base = `${environment.apiUrl}/api/chats`;

  health(): Observable<Health> {
    return this.http.get<Health>(`${this.base}/health/`);
  }

  listChats(): Observable<ChatSummary[]> {
    return this.http.get<ChatSummary[]>(`${this.base}/list/`, {
      params: { session_id: this.session.sessionId },
    });
  }

  createChat(): Observable<{ id: string; title: string }> {
    return this.http.post<{ id: string; title: string }>(`${this.base}/`, {
      session_id: this.session.sessionId,
    });
  }

  getChat(chatId: string): Observable<Chat> {
    return this.http.get<Chat>(`${this.base}/${chatId}/`);
  }

  sendMessage(chatId: string, content: string): Observable<SendMessageResponse> {
    return this.http.post<SendMessageResponse>(
      `${this.base}/${chatId}/messages/`,
      { content },
    );
  }

  deleteChat(chatId: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/${chatId}/`);
  }
}
