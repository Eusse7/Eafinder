import { Injectable, computed, signal } from '@angular/core';

export type Theme = 'light' | 'dark';

export const THEME_STORAGE_KEY = 'eafinder_theme';

/**
 * Servicio de gestión de tema (US19: Cambio entre tema claro y oscuro).
 *
 * Persiste la preferencia en localStorage, detecta la preferencia del sistema
 * (prefers-color-scheme) y aplica la clase/atributo data-theme en el elemento raíz
 * sin recargar la página ni perder el estado de la conversación activa.
 */
@Injectable({ providedIn: 'root' })
export class ThemeService {
  readonly theme = signal<Theme>(this.getInitialTheme());
  readonly isDark = computed(() => this.theme() === 'dark');

  constructor() {
    this.applyTheme(this.theme());
  }

  toggleTheme(): void {
    const next: Theme = this.theme() === 'dark' ? 'light' : 'dark';
    this.setTheme(next);
  }

  setTheme(newTheme: Theme): void {
    this.theme.set(newTheme);

    if (typeof localStorage !== 'undefined') {
      try {
        localStorage.setItem(THEME_STORAGE_KEY, newTheme);
      } catch {
        // Ignora si localStorage está bloqueado o en modo privado estricto
      }
    }

    this.applyTheme(newTheme);
  }

  private getInitialTheme(): Theme {
    if (typeof window === 'undefined') {
      return 'light';
    }

    try {
      const stored = localStorage.getItem(THEME_STORAGE_KEY);
      if (stored === 'light' || stored === 'dark') {
        return stored;
      }
    } catch {
      // Fallback a claro si localStorage no está disponible
    }

    // Por defecto institucional, siempre inicia en tema claro
    return 'light';
  }

  private applyTheme(theme: Theme): void {
    if (typeof document === 'undefined') {
      return;
    }

    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.style.colorScheme = theme;

    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    const color = theme === 'dark' ? '#0b0f19' : '#eef2ff';
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', color);
    }
  }
}
