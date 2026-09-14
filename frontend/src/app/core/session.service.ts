import { Injectable } from '@angular/core';

const SESSION_KEY = 'eafit_session_id';

/**
 * EAFinder no tiene cuentas de usuario (SRS 1.4-f). Para poder separar las
 * conversaciones de una persona de las de otra se usa un identificador
 * anónimo guardado en sessionStorage, que desaparece al cerrar la pestaña
 * (US01: la conversación no persiste más allá de la sesión).
 */
@Injectable({ providedIn: 'root' })
export class SessionService {
  readonly sessionId = this.load();

  private load(): string {
    let id = sessionStorage.getItem(SESSION_KEY);

    if (!id) {
      id = crypto.randomUUID();
      sessionStorage.setItem(SESSION_KEY, id);
    }

    return id;
  }
}
