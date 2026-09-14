/** Tipos que devuelve la API de Django. */

export interface Source {
  id: string;
  label: string;
  document_title: string;
  article_ref: string;
  excerpt: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
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
