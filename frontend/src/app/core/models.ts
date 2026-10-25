/** Tipos que devuelve la API de Django. */

export interface Source {
  id: string;
  label: string;
  document_title: string;
  article_ref: string;
  excerpt: string;
}

export type Feedback = 'up' | 'down' | '';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  /** US15: valoración del usuario sobre la respuesta ('' = sin valorar). */
  feedback: Feedback;
  /** US20: respuesta generada por el filtro de moderación. */
  moderated: boolean;
  sources: Source[];
}

export interface ChatSummary {
  id: string;
  title: string;
  created_at: string;
}

export interface Chat {
  id: string;
  title: string;
  created_at: string;
  messages: Message[];
  has_more: boolean;
  next_cursor: string | null;
}

export interface SendMessageResponse {
  user_message: Message;
  assistant_message: Message;
  chat_title: string;
}

export interface Health {
  status: string;
  documents: number;
  chunks: number;
  ai_provider: string;
  ai_configured: boolean;
}

/** US05: métricas del panel de analítica de búsquedas. */
export interface TopicMetric {
  topic: string;
  count: number;
  percentage: number;
}

export interface DailyVolume {
  date: string;
  count: number;
}

/** US18: reporte y alertas de brechas de conocimiento. */
export interface KnowledgeGapItem {
  query: string;
  normalized_query: string;
  count: number;
  last_asked: string;
  avg_similarity: number;
  is_recurring: boolean;
}

export interface KnowledgeGapsReport {
  has_gaps: boolean;
  total_gaps: number;
  pending_gaps: number;
  has_alerts: boolean;
  recurring_gaps: KnowledgeGapItem[];
}

export interface AnalyticsData {
  has_data: boolean;
  total_queries: number;
  total_chats: number;
  satisfaction_rate: number | null;
  feedback_up: number;
  feedback_down: number;
  moderated_queries: number;
  frequent_topics: TopicMetric[];
  daily_volume: DailyVolume[];
  knowledge_gaps?: KnowledgeGapsReport;
}

