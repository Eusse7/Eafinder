import { useState } from 'react';
import { X } from 'lucide-react';
import { useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

import { deleteChat } from '@api/chats';
import DeleteChatModal from './DeleteChatModal';
import { useChats } from '../utils/api/useChats';

export default function Chats() {
  const { data: chats = [], isLoading } = useChats();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const [chatToDelete, setChatToDelete] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  async function handleDelete() {
    if (!chatToDelete) {
      return;
    }

    setIsDeleting(true);

    try {
      await deleteChat(chatToDelete);

      await queryClient.invalidateQueries({
        queryKey: ['chats'],
      });

      setChatToDelete(null);
      navigate('/');
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <>
      <div className="flex-1 overflow-y-auto border-b border-gray-200 px-3 py-4">
        <h2 className="px-2 pb-2 text-xs font-semibold tracking-wide text-gray-500">
          Recientes
        </h2>

        <div className="flex flex-col gap-1">
          {isLoading ? (
            <p className="px-2 py-2 text-sm text-gray-400">Cargando...</p>
          ) : (
            chats.map((chat) => (
              <div
                key={chat.id}
                onClick={() => navigate(`/chat/${chat.id}`)}
                className="group flex cursor-pointer items-center justify-between gap-2 rounded-lg px-2 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-100"
              >
                <span className="truncate">{chat.title}</span>

                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    setChatToDelete(chat.id);
                  }}
                  className="flex h-5 w-5 shrink-0 cursor-pointer items-center justify-center rounded-full text-gray-400 transition-all hover:bg-gray-300 hover:text-gray-700"
                  aria-label="Eliminar conversación"
                >
                  <X size={13} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      <DeleteChatModal
        isOpen={chatToDelete !== null}
        isDeleting={isDeleting}
        onCancel={() => setChatToDelete(null)}
        onConfirm={handleDelete}
      />
    </>
  );
}
