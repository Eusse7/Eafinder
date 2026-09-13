import { createChat, sendMessage } from '@api/chats';

export async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
  event.preventDefault();

  const textarea = event.currentTarget.querySelector('textarea');
  const query = textarea?.value.trim();

  if (!query) {
    return;
  }

  const chatId = await createChat();

  await sendMessage(chatId, query);

  window.location.assign(`/chat/${chatId}`);
}
