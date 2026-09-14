import { Component, OnInit, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { ChatStore } from './core/chat.store';
import { Composer } from './layout/composer';
import { Sidebar } from './layout/sidebar';
import { Topbar } from './layout/topbar';

/** Interfaz centralizada de EAFinder (US03). */
@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Sidebar, Topbar, Composer],
  templateUrl: './app.html',
})
export class App implements OnInit {
  protected readonly store = inject(ChatStore);
  protected sidebarOpen = window.innerWidth >= 640;

  ngOnInit(): void {
    this.store.checkHealth();
    this.store.loadChats();

    // Revisa periódicamente si el backend sigue disponible (US11).
    setInterval(() => this.store.checkHealth(), 15000);
  }

  toggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
  }

  closeSidebar(): void {
    this.sidebarOpen = false;
  }
}
