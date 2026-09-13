import { Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function NewConversationButton() {
  const navigate = useNavigate();

  return (
    <button
      type="button"
      onClick={() => navigate('/')}
      className="m-4 flex h-10 cursor-pointer items-center rounded-xl bg-blue-950/95 text-white shadow-[0_0_10px_rgba(0,0,0,0.2)] hover:opacity-85 max-sm:h-9"
    >
      <div className="pl-3 pr-3">
        <Plus size={20} />
      </div>

      <p className="flex-1 text-left">Nueva conversación</p>
    </button>
  );
}
