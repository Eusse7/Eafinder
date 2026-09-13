import {
  BookOpen,
  CalendarDays,
  GraduationCap,
  Heart,
  Landmark,
  Wallet,
  type LucideIcon,
} from 'lucide-react';

export interface CardData {
  icon: LucideIcon;
  title: string;
  content: string;
  prompt: string;
}

export function getCards(): CardData[] {
  return [
    {
      icon: BookOpen,
      title: 'Trámites de matrícula',
      content: 'Proceso, fechas y requisitos de inscripción',
      prompt: '¿Cómo realizo mi proceso de matrícula?',
    },
    {
      icon: GraduationCap,
      title: 'Proceso de grado',
      content: 'Requisitos y etapas para graduarte',
      prompt: '¿Cuál es el proceso para graduarme de EAFIT?',
    },
    {
      icon: Wallet,
      title: 'Pagos y financiación',
      content: 'Opciones de pago, becas y créditos',
      prompt: '¿Cuáles son las opciones de pago y financiación disponibles?',
    },
    {
      icon: CalendarDays,
      title: 'Calendario académico',
      content: 'Fechas clave del semestre en curso',
      prompt:
        '¿Cuáles son las fechas importantes del calendario académico 2026?',
    },
    {
      icon: Landmark,
      title: 'Oferta académica',
      content: 'Programas de pregrado y posgrado',
      prompt: '¿Qué programas académicos ofrece la Universidad EAFIT?',
    },
    {
      icon: Heart,
      title: 'Bienestar universitario',
      content: 'Servicios de salud, deporte y apoyo',
      prompt: '¿Qué servicios ofrece Bienestar Universitario de EAFIT?',
    },
  ];
}
