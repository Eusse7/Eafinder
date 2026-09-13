import { useQueryClient } from '@tanstack/react-query';
import { ChevronRight } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { createChat, sendMessage } from '@api/chats';

interface CardProps {
  icon: LucideIcon;
  title: string;
  content: string;
  prompt: string;
}

export default function Card({ icon, title, content, prompt }: CardProps) {
  const Icon = icon;
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  async function handleClick() {
    const chatId = await createChat();

    await sendMessage(chatId, prompt);

    await queryClient.invalidateQueries({
      queryKey: ['chats'],
    });

    navigate(`/chat/${chatId}`);
  }

  return (
    <section
      onClick={handleClick}
      className="group flex h-20 w-36/37 cursor-pointer items-center gap-3 overflow-hidden rounded-2xl border border-gray-200 bg-white pl-4 shadow-[0_0_0_rgba(0,0,0,0)] transition-all duration-200 hover:border-blue-900 hover:shadow-[0_0_10px_rgba(37,99,235,0.12)]"
    >
      <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-gray-100 bg-indigo-50 text-blue-900">
        <Icon />
      </div>

      <div className="flex min-w-0 flex-1 flex-col">
        <div className="flex items-center justify-between pr-3">
          <h3 className="font-semibold">{title}</h3>

          <div className="text-gray-900 transition-colors duration-200 group-hover:text-blue-900">
            <ChevronRight
              size={17}
              strokeWidth={0.5}
              className="transition-[stroke-width] duration-200 group-hover:stroke-2"
            />
          </div>
        </div>

        <p className="overflow-x-hidden text-sm text-gray-500">{content}</p>
      </div>
    </section>
  );
}
