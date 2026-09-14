import { Component, inject } from '@angular/core';

import { ChatStore } from '../../core/chat.store';

interface Suggestion {
  icon: string;
  title: string;
  description: string;
  prompt: string;
}

/**
 * Pantalla inicial (US03): un único punto de entrada que además reúne los
 * enlaces a los portales institucionales esenciales.
 *
 * Las sugerencias son preguntas que SÍ se pueden responder desde el
 * Reglamento Académico. Preguntas sobre tarifas o fechas del calendario
 * quedan fuera de alcance por diseño (SRS 1.4-c), así que no se sugieren.
 */
@Component({
  selector: 'app-welcome',
  templateUrl: './welcome.page.html',
})
export class WelcomePage {
  protected readonly store = inject(ChatStore);

  protected readonly suggestions: Suggestion[] = [
    {
      icon: '📝',
      title: 'Matrícula',
      description: 'Condiciones y requisitos que fija el reglamento',
      prompt: '¿Qué dice el reglamento sobre el proceso de matrícula?',
    },
    {
      icon: '🚫',
      title: 'Cancelación de asignaturas',
      description: 'Plazos y condiciones para cancelar',
      prompt: '¿Hasta cuándo puedo cancelar una asignatura y qué condiciones aplican?',
    },
    {
      icon: '⚠️',
      title: 'Prueba académica',
      description: 'Cuándo se entra y cómo se sale',
      prompt: '¿Cuándo queda un estudiante en prueba académica?',
    },
    {
      icon: '🎓',
      title: 'Requisitos de grado',
      description: 'Condiciones para optar al título',
      prompt: '¿Cuáles son los requisitos para optar al título de pregrado?',
    },
    {
      icon: '🔁',
      title: 'Homologación de materias',
      description: 'Validaciones y reconocimiento de créditos',
      prompt: '¿Cómo funciona la homologación de asignaturas según el reglamento?',
    },
    {
      icon: '📄',
      title: 'Reclamo de notas',
      description: 'Procedimiento y plazos para solicitar revisión',
      prompt: '¿Cuál es el procedimiento para solicitar la revisión de una nota?',
    },
  ];

  protected readonly links = [
    { label: 'Portal EAFIT', url: 'https://www.eafit.edu.co/' },
    { label: 'Reglamentos', url: 'https://www.eafit.edu.co/institucional/reglamentos' },
    { label: 'Epik', url: 'https://www.eafit.edu.co/epik' },
    { label: 'EAFIT Interactiva', url: 'https://interactiva.eafit.edu.co/' },
    { label: 'Admisiones y Registro', url: 'https://www.eafit.edu.co/admisiones' },
  ];

  ask(prompt: string): void {
    this.store.ask(prompt);
  }
}
