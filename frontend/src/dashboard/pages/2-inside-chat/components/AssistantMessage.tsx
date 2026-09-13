import { Sparkles } from 'lucide-react';

interface AssistantMessageProps {
  content: string;
}

export default function AssistantMessage({ content }: AssistantMessageProps) {
  const time = new Date().toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="flex items-end justify-start gap-2">
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-950 p-1.5 text-white">
        <Sparkles size={15} />
      </div>

      <div className="max-w-[75%] rounded-2xl rounded-bl-none bg-white px-4 py-3 text-gray-900 shadow-sm">
        <p className="whitespace-pre-wrap">{content}</p>
        <p className="mt-1 text-left text-xs text-gray-400">{time}</p>
      </div>
    </div>
  );
}
