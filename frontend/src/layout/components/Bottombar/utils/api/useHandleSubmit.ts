import { useQueryClient } from '@tanstack/react-query';
import { useLocation, useNavigate } from 'react-router-dom';

import { createChat, sendMessage } from '@api/chats';

export function useHandleSubmit() {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();

  return async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const textarea = event.currentTarget.querySelector('textarea');
    const query = textarea?.value.trim();

    if (!query) {
      return;
    }

    if (textarea) {
      textarea.value = '';
    }

    const chatId = location.pathname.startsWith('/chat/')
      ? location.pathname.split('/')[2]
      : undefined;

    if (chatId) {
      await sendMessage(chatId, query);

      await queryClient.invalidateQueries({
        queryKey: ['chat', chatId],
      });

      return;
    }

    const newChatId = await createChat();

    await sendMessage(newChatId, query);

    await queryClient.invalidateQueries({
      queryKey: ['chats'],
    });

    navigate(`/chat/${newChatId}`);
  };
}
