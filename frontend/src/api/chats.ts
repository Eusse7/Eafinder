import axios from 'axios';

import { showChatLimitToast } from '../layout/components/Sidebar/utils/showChatLimitToast';
import { getSessionId } from '../utils/getSessionId';

const API_URL = import.meta.env.VITE_API_URL;

const api = axios.create({
  baseURL: API_URL,
});

export async function createChat(): Promise<string> {
  try {
    const response = await api.post<{ id: string }>('/api/chats/', {
      session_id: getSessionId(),
    });

    return response.data.id;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 400) {
      showChatLimitToast();
    }

    throw error;
  }
}

export interface ChatSummary {
  id: string;
  title: string;
  created_at: string;
}

export async function getChats(): Promise<ChatSummary[]> {
  const response = await api.get<ChatSummary[]>('/api/chats/list/', {
    params: {
      session_id: getSessionId(),
    },
  });

  return response.data;
}

export async function sendMessage(
  chatId: string,
  content: string,
): Promise<void> {
  await api.post(`/api/chats/${chatId}/messages/`, {
    content,
  });
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
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

export async function getChat(chatId: string, before?: string): Promise<Chat> {
  const response = await api.get<Chat>(`/api/chats/${chatId}/`, {
    params: before ? { before } : undefined,
  });

  return response.data;
}

export async function chatExists(chatId: string): Promise<boolean> {
  const response = await api.get<{ exists: boolean }>(
    `/api/chats/${chatId}/exists/`,
  );

  return response.data.exists;
}

export async function deleteChat(chatId: string): Promise<void> {
  await api.delete(`/api/chats/${chatId}/`);
}
