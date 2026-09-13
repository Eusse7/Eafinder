interface UserMessageProps {
  content: string;
}

export default function UserMessage({ content }: UserMessageProps) {
  const time = new Date().toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="flex justify-end">
      <div className="max-w-[75%] rounded-2xl rounded-br-none bg-blue-950 px-4 py-3 text-white">
        <p>{content}</p>

        <p className="mt-1 text-right text-xs text-white/60">{time}</p>
      </div>
    </div>
  );
}
