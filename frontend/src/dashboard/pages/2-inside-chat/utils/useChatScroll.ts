import { useLayoutEffect, useRef } from 'react';

interface UseChatScrollParams {
  messagesLength: number;
  hasNextPage: boolean;
  isFetchingNextPage: boolean;
  messages: unknown[];
}

export function useChatScroll({
  messagesLength,
  hasNextPage,
  isFetchingNextPage,
  messages,
}: UseChatScrollParams) {
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  const isInitialLoadRef = useRef(true);
  const isLoadingOlderRef = useRef(false);

  const previousScrollHeightRef = useRef(0);
  const previousScrollTopRef = useRef(0);

  const previousMessageCountRef = useRef(0);
  const shouldAutoScrollRef = useRef(true);

  useLayoutEffect(() => {
    const container = messagesContainerRef.current;

    if (!container || !messagesLength) {
      return;
    }

    if (isInitialLoadRef.current) {
      container.scrollTop = container.scrollHeight;

      isInitialLoadRef.current = false;
      previousMessageCountRef.current = messagesLength;

      return;
    }

    if (isLoadingOlderRef.current) {
      container.scrollTop =
        container.scrollHeight -
        previousScrollHeightRef.current +
        previousScrollTopRef.current;

      isLoadingOlderRef.current = false;
      previousMessageCountRef.current = messagesLength;

      return;
    }

    if (messagesLength > previousMessageCountRef.current) {
      if (shouldAutoScrollRef.current) {
        requestAnimationFrame(() => {
          container.scrollTop = container.scrollHeight;

          requestAnimationFrame(() => {
            container.scrollTop = container.scrollHeight;
          });
        });
      }

      previousMessageCountRef.current = messagesLength;
    }
  }, [messagesLength]);

  useLayoutEffect(() => {
    const container = messagesContainerRef.current;

    if (
      !container ||
      isInitialLoadRef.current ||
      isLoadingOlderRef.current ||
      !shouldAutoScrollRef.current ||
      !messagesLength
    ) {
      return;
    }

    const distanceFromBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight;

    if (distanceFromBottom <= 100) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages, messagesLength]);

  async function loadOlderMessages(fetchNextPage: () => Promise<unknown>) {
    const container = messagesContainerRef.current;

    if (
      !container ||
      !hasNextPage ||
      isFetchingNextPage ||
      isLoadingOlderRef.current
    ) {
      return;
    }

    isLoadingOlderRef.current = true;

    previousScrollHeightRef.current = container.scrollHeight;
    previousScrollTopRef.current = container.scrollTop;

    await fetchNextPage();
  }

  function handleScroll(fetchNextPage: () => Promise<unknown>) {
    const container = messagesContainerRef.current;

    if (!container) {
      return;
    }

    const distanceFromBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight;

    shouldAutoScrollRef.current = distanceFromBottom <= 100;

    if (container.scrollTop <= 50) {
      loadOlderMessages(fetchNextPage);
    }
  }

  return {
    messagesContainerRef,
    handleScroll,
  };
}
