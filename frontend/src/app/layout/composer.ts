import { Component, ElementRef, ViewChild, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ChatStore } from '../core/chat.store';

/** Campo de consulta. Vive en el layout para estar disponible en toda la app. */
@Component({
  selector: 'app-composer',
  imports: [FormsModule],
  template: `
    <footer class="composer">
      <form class="composer-box" (submit)="submit($event)">
        <textarea
          #input
          [(ngModel)]="text"
          name="question"
          rows="1"
          class="composer-input"
          placeholder="Escribe tu consulta aquí…"
          [disabled]="store.sending()"
          (input)="autoGrow()"
          (keydown)="onKeydown($event)"
        ></textarea>

        <button
          type="submit"
          class="send-button"
          [disabled]="!text.trim() || store.sending()"
          aria-label="Enviar consulta"
        >
          ↑
        </button>
      </form>

      <p class="composer-note">
        Asistente especializado en los reglamentos y trámites de la
        <strong>Universidad EAFIT</strong>
      </p>
    </footer>
  `,
})
export class Composer {
  @ViewChild('input') inputRef?: ElementRef<HTMLTextAreaElement>;

  protected readonly store = inject(ChatStore);
  protected text = '';

  async submit(event: Event): Promise<void> {
    event.preventDefault();

    const question = this.text;
    this.text = '';
    this.resetHeight();

    await this.store.ask(question);
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      (event.target as HTMLTextAreaElement).form?.requestSubmit();
    }
  }

  autoGrow(): void {
    const element = this.inputRef?.nativeElement;

    if (!element) {
      return;
    }

    element.style.height = 'auto';
    element.style.height = `${Math.min(element.scrollHeight, 160)}px`;
  }

  private resetHeight(): void {
    const element = this.inputRef?.nativeElement;

    if (element) {
      element.style.height = 'auto';
    }
  }
}
