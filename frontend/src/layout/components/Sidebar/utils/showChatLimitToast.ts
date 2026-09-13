const CHAT_LIMIT_EVENT = 'chat-limit-reached';

export function showChatLimitToast() {
  window.dispatchEvent(new Event(CHAT_LIMIT_EVENT));
}

export function onChatLimitToast(callback: () => void) {
  window.addEventListener(CHAT_LIMIT_EVENT, callback);

  return () => {
    window.removeEventListener(CHAT_LIMIT_EVENT, callback);
  };
}
