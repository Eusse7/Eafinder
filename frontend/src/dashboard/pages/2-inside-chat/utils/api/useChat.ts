import { useInfiniteQuery } from '@tanstack/react-query';

import { getChat } from '@api/chats';

export function useChat(chatId: string | undefined) {
  return useInfiniteQuery({
    queryKey: ['chat', chatId],
    queryFn: ({ pageParam }) => getChat(chatId!, pageParam),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) =>
      lastPage.has_more ? lastPage.next_cursor : undefined,
    enabled: !!chatId,
  });
}
