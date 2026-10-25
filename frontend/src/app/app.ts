import { Component, HostListener, OnInit, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { ChatStore } from './core/chat.store';
import { Composer } from './layout/composer';
import { Sidebar } from './layout/sidebar';
import { Topbar } from './layout/topbar';

/** Interfaz centralizada y responsiva de EAFinder (US03, US06). */
@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Sidebar, Topbar, Composer],
  templateUrl: './app.html',
})
export class App implements OnInit {
  protected readonly store = inject(ChatStore);
  /** En pantallas grandes (>=1024px) la barra lateral inicia abierta; en móviles y tabletas cerrada. */
  protected sidebarOpen = typeof window !== 'undefined' ? window.innerWidth >= 1024 : false;
  private previousWidth = typeof window !== 'undefined' ? window.innerWidth : 1024;

  ngOnInit(): void {
    this.store.checkHealth();
    this.store.loadChats();

    // Revisa periódicamente si el backend sigue disponible (US11).
    setInterval(() => this.store.checkHealth(), 15000);
  }

  /** Adapta dinámicamente el estado de la barra lateral al cambiar el tamaño de ventana o girar el dispositivo. */
  @HostListener('window:resize')
  onResize(): void {
    if (typeof window === 'undefined') {
      return;
    }
    const currentWidth = window.innerWidth;

    if (currentWidth < 1024 && this.previousWidth >= 1024) {
      this.sidebarOpen = false;
    } else if (currentWidth >= 1024 && this.previousWidth < 1024) {
      this.sidebarOpen = true;
    }

    this.previousWidth = currentWidth;
  }

  /** Permite cerrar la barra lateral móvil con la tecla Escape. */
  @HostListener('window:keydown.escape')
  onEscape(): void {
    if (typeof window !== 'undefined' && window.innerWidth < 1024 && this.sidebarOpen) {
      this.sidebarOpen = false;
    }
  }

  toggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }

  closeSidebar(): void {
    this.sidebarOpen = false;
  }
}

