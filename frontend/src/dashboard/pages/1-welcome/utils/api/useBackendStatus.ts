import { useQuery } from '@tanstack/react-query';

import { getChats } from '@api/chats';

export function useBackendStatus() {
  return useQuery({
    queryKey: ['backend-status'],
    queryFn: getChats,
    retry: false,
    refetchInterval: 5000,
  });
}
