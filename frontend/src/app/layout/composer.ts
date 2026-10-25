import {
  ChangeDetectorRef,
  Component,
  ElementRef,
  NgZone,
  OnDestroy,
  ViewChild,
  inject,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ChatStore } from '../core/chat.store';

/** Campo de consulta y dictado por voz (US14). Vive en el layout para estar disponible en toda la app. */
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
          [placeholder]="
            listening()
              ? 'Escuchando tu pregunta… (habla ahora)'
              : 'Escribe tu consulta aquí…'
          "
          [disabled]="store.sending()"
          (input)="autoGrow()"
          (keydown)="onKeydown($event)"
        ></textarea>

        <button
          type="button"
          class="mic-button"
          [class.mic-active]="listening()"
          (click)="toggleListening()"
          [disabled]="store.sending()"
          [attr.aria-label]="
            listening() ? 'Detener dictado por voz' : 'Dictar pregunta por voz'
          "
          [attr.title]="
            listening()
              ? 'Detener dictado por voz'
              : 'Dictar pregunta por voz (US14)'
          "
        >
          @if (listening()) {
            <div class="mic-wave" aria-hidden="true">
              <span></span><span></span><span></span>
            </div>
          } @else {
            <svg
              class="mic-icon"
              viewBox="0 0 24 24"
              fill="currentColor"
              width="20"
              height="20"
              aria-hidden="true"
            >
              <path
                d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"
              />
              <path
                d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"
              />
            </svg>
          }
        </button>

        <button
          type="submit"
          class="send-button"
          [disabled]="!text.trim() || store.sending()"
          aria-label="Enviar consulta"
        >
          ↑
        </button>
      </form>

      <div
        class="composer-listening-bar"
        [class.visible]="listening()"
        aria-live="polite"
      >
        <div class="sound-wave" aria-hidden="true">
          <span></span><span></span><span></span><span></span>
        </div>
        <span class="listening-text">
          Escuchando… Dicta tu pregunta y aparecerá en el campo.
        </span>
        <button
          type="button"
          class="stop-listening-btn"
          (click)="stopListening()"
          aria-label="Detener escucha"
        >
          Detener
        </button>
      </div>

      <p class="composer-note">
        Asistente especializado en los reglamentos y trámites de la
        <strong>Universidad EAFIT</strong>
      </p>
    </footer>
  `,
})
export class Composer implements OnDestroy {
  @ViewChild('input') inputRef?: ElementRef<HTMLTextAreaElement>;

  protected readonly store = inject(ChatStore);
  private readonly ngZone = inject(NgZone);
  private readonly cdr = inject(ChangeDetectorRef);

  protected text = '';
  protected readonly listening = signal(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private recognition: any = null;

  ngOnDestroy(): void {
    this.stopListening();
  }

  toggleListening(): void {
    if (this.listening()) {
      this.stopListening();
    } else {
      this.startListening();
    }
  }

  private startListening(): void {
    if (typeof window === 'undefined') {
      return;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const SpeechRecognitionClass =
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognitionClass) {
      // Escenario 2: navegador sin soporte para entrada de voz
      this.store.showToast(
        'Tu navegador no admite dictado de voz. Puedes escribir tu consulta manualmente.',
      );
      return;
    }

    // Abortar de forma segura cualquier instancia anterior que pudiera haber quedado activa
    if (this.recognition) {
      try {
        this.recognition.abort();
      } catch {
        // Ignorar
      }
      this.recognition = null;
    }

    // Activación reactiva instantánea para que la animación responda de inmediato al clic
    this.listening.set(true);
    this.cdr.markForCheck();

    try {
      this.recognition = new SpeechRecognitionClass();
      this.recognition.lang = 'es-CO';
      this.recognition.interimResults = true;
      this.recognition.continuous = false;

      this.recognition.onstart = () => {
        this.ngZone.run(() => {
          this.listening.set(true);
          this.cdr.markForCheck();
        });
      };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      this.recognition.onresult = (event: any) => {
        this.ngZone.run(() => {
          let transcript = '';
          for (let i = 0; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
          }
          if (transcript.trim()) {
            this.text = transcript;
            this.autoGrow();
            this.cdr.markForCheck();
          }
        });
      };

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      this.recognition.onerror = (event: any) => {
        this.ngZone.run(() => {
          this.listening.set(false);
          this.cdr.markForCheck();
          // Escenario 2: permiso denegado o voz no reconocida
          if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
            this.store.showToast(
              'Permiso de micrófono denegado. Permite el acceso o escribe tu pregunta.',
            );
          } else if (event.error === 'no-speech') {
            this.store.showToast(
              'No se reconoció ninguna voz. Intenta dictar nuevamente o escribe tu pregunta.',
            );
          } else {
            this.store.showToast(
              'No fue posible reconocer la voz. Por favor, escribe tu consulta.',
            );
          }
        });
      };

      this.recognition.onend = () => {
        this.ngZone.run(() => {
          this.listening.set(false);
          this.cdr.markForCheck();
        });
      };

      this.recognition.start();
    } catch {
      this.listening.set(false);
      this.cdr.markForCheck();
      this.store.showToast(
        'No fue posible iniciar el micrófono. Puedes escribir tu consulta.',
      );
    }
  }

  stopListening(): void {
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch {
        // Ignorar si ya finalizó
      }
      this.recognition = null;
    }
    this.listening.set(false);
    this.cdr.markForCheck();
  }

  async submit(event: Event): Promise<void> {
    event.preventDefault();

    if (this.listening()) {
      this.stopListening();
    }

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
