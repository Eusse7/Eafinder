import { Component, EventEmitter, Output, inject } from '@angular/core';

import { ChatStore } from '../core/chat.store';
import { ThemeService } from '../core/theme.service';

@Component({
  selector: 'app-topbar',
  template: `
    <header class="topbar">
      <button
        type="button"
        class="icon-button topbar-menu"
        (click)="menuClick.emit()"
        aria-label="Abrir o cerrar barra lateral"
      >
        ☰
      </button>

      <span class="topbar-mark">✦</span>
      <p class="topbar-title">Asistente EAFIT</p>
      <span class="badge">IA</span>

      <div class="topbar-actions">
        @if (!store.backendOnline()) {
          <span class="status status-offline" title="Sin conexión con el backend">
            <span class="offline-full">Sin conexión con el backend</span>
            <span class="offline-short">Sin conexión</span>
          </span>
        }

        <button
          type="button"
          class="icon-button theme-toggle-btn"
          (click)="theme.toggleTheme()"
          [attr.aria-label]="theme.isDark() ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'"
          [attr.title]="theme.isDark() ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'"
        >
          @if (theme.isDark()) {
            <svg class="theme-icon sun-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
              <line x1="1" y1="12" x2="3" y2="12"></line>
              <line x1="21" y1="12" x2="23" y2="12"></line>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
          } @else {
            <svg class="theme-icon moon-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg>
          }
        </button>
      </div>
    </header>
  `,
})
export class Topbar {
  @Output() menuClick = new EventEmitter<void>();
  protected readonly store = inject(ChatStore);
  protected readonly theme = inject(ThemeService);
}
