import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

import { chatExists } from '@api/chats';
import { useChat } from '../utils/api/useChat';
import { getMessages } from '../utils/getMessages';
import { useChatScroll } from '../utils/useChatScroll';

import AssistantMessage from './AssistantMessage';
import UserMessage from './UserMessage';

export default function InsideChat() {
  const { chatId } = useParams();
  const navigate = useNavigate();

  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useChat(chatId);

  useEffect(() => {
    if (!chatId) {
      navigate('/', { replace: true });
      return;
    }

    async function checkChat() {
      try {
        const exists = await chatExists(chatId!);

        if (!exists) {
          navigate('/', { replace: true });
        }
      } catch {
        navigate('/', { replace: true });
      }
    }

    checkChat();
  }, [chatId, navigate]);

  const pages = data?.pages ?? [];
  const messages = getMessages(pages);

  const { messagesContainerRef, handleScroll } = useChatScroll({
    messagesLength: messages.length,
    hasNextPage: !!hasNextPage,
    isFetchingNextPage,
    messages,
  });

  return (
    <div className="flex h-full min-h-0 w-full flex-col bg-indigo-50/80">
      <div
        ref={messagesContainerRef}
        onScroll={() => handleScroll(fetchNextPage)}
        className="min-h-0 flex-1 overflow-y-auto px-8 py-6"
      >
        <div className="mx-auto flex max-w-4xl flex-col gap-4">
          {messages.map((message) =>
            message.role === 'user' ? (
              <UserMessage key={message.id} content={message.content} />
            ) : (
              <AssistantMessage key={message.id} content={message.content} />
            ),
          )}

          {isFetchingNextPage && (
            <p className="py-2 text-center text-sm text-gray-400">
              Cargando mensajes anteriores...
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
