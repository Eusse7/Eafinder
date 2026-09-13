import { Menu, Sparkles } from 'lucide-react';

interface TopbarProps {
  sidebarStatus: boolean;
  setSidebarStatus: React.Dispatch<React.SetStateAction<boolean>>;
}

export default function Topbar({
  sidebarStatus,
  setSidebarStatus,
}: TopbarProps) {
  return (
    <div className="flex h-14 items-center gap-4 border-b border-gray-200 bg-indigo-50/80 pl-4">
      <div
        onClick={() => setSidebarStatus(!sidebarStatus)}
        className="flex h-6 w-6 cursor-pointer items-center justify-center text-gray-800 hover:rounded-xl hover:bg-gray-200 hover:text-black"
      >
        <Menu strokeWidth={1} size={15} />
      </div>

      <div className="flex h-5 w-5 translate-x-2 items-center justify-center rounded-sm bg-blue-950 text-white">
        <Sparkles strokeWidth={1.5} size={13} />
      </div>

      <p className="truncate font-semibold">Asistente EAFIT</p>

      <span className="flex h-4 w-6 items-center justify-center rounded border border-gray-200 bg-white pl-1 text-xs text-gray-500">
        IA
      </span>
    </div>
  );
}
