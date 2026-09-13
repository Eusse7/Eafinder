import { useRef, useState } from 'react';
import { ArrowUp } from 'lucide-react';

import { handleTextareaInput } from '../utils/handleTextareaInput';
import { useHandleSubmit } from '../utils/api/useHandleSubmit';

export default function Bottombar() {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [hasText, setHasText] = useState(false);
  const handleSubmit = useHandleSubmit();

  return (
    <footer className="flex flex-col items-center px-8 pt-5">
      <form
        className="flex w-full items-end justify-between rounded-xl bg-white px-4 py-3 shadow-[0_0_8px_rgba(0,0,0,0.2)]"
        onSubmit={handleSubmit}
      >
        <textarea
          ref={textareaRef}
          onInput={() => handleTextareaInput(textareaRef.current, setHasText)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }}
          className="max-h-40 flex-1 resize-none overflow-y-auto outline-none placeholder:text-gray-500 leading-7 placeholder:truncate"
          placeholder="Escribe tu consulta aquí..."
          rows={1}
        />

        <button
          type="submit"
          disabled={!hasText}
          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-4xl text-white transition-all duration-200 ${
            hasText
              ? 'cursor-pointer bg-blue-950 shadow-[0_0_9px_rgba(0,0,0,0.3)]'
              : 'cursor-not-allowed bg-blue-950/35 shadow-none'
          }`}
        >
          <ArrowUp size={18} />
        </button>
      </form>

      <p className="pb-4 pt-2 text-sm text-gray-500 text-center max-sm:text-xs">
        Asistente especializado en servicios y trámites de la{' '}
        <strong className="text-gray-700">Universidad EAFIT</strong>
      </p>
    </footer>
  );
}
