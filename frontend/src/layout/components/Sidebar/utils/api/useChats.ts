import { useQuery } from '@tanstack/react-query';

import { getChats } from '@api/chats';

export function useChats() {
  return useQuery({
    queryKey: ['chats'],
    queryFn: getChats,
    retry: false,
    refetchInterval: 5000,
  });
}
