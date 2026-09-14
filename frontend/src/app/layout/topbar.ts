import { Component, EventEmitter, Output, inject } from '@angular/core';

import { ChatStore } from '../core/chat.store';

@Component({
  selector: 'app-topbar',
  template: `
    <header class="topbar">
      <button type="button" class="icon-button" (click)="menuClick.emit()" aria-label="Menú">
        ☰
      </button>

      <span class="topbar-mark">✦</span>
      <p class="topbar-title">Asistente EAFIT</p>
      <span class="badge">IA</span>

      @if (!store.backendOnline()) {
        <span class="status status-offline">Sin conexión con el backend</span>
      }
    </header>
  `,
})
export class Topbar {
  @Output() menuClick = new EventEmitter<void>();
  protected readonly store = inject(ChatStore);
}
