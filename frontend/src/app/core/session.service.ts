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
      id = this.generateUUID();
      sessionStorage.setItem(SESSION_KEY, id);
    }

    return id;
  }

  /**
   * Genera un UUID v4. Usa crypto.randomUUID() cuando está disponible
   * (contextos seguros: HTTPS o localhost). En HTTP puro usa un fallback
   * basado en Math.random(), suficiente para un identificador de sesión anónimo.
   */
  private generateUUID(): string {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID();
    }
    // Fallback para contextos no-seguros (HTTP con IP directa)
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  }
}
