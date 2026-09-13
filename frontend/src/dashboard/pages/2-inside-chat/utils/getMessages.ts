import type { Chat } from '@api/chats';

export function getMessages(pages: Chat[]) {
  return pages
    .flatMap((page) => page.messages)
    .sort(
      (a, b) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
    );
}
