import logoEafitNegro from '../assets/logoEafitNegro.jpg';

import { useBackendStatus } from '../utils/api/useBackendStatus';

export default function Header() {
  const { isError } = useBackendStatus();

  return (
    <header className="flex h-full w-full flex-col items-center gap-3 text-center">
      <div className="relative mt-5 flex h-20 w-44 justify-center rounded-2xl bg-white shadow-[0_0_20px_rgba(0,0,0,0.2)]">
        <img
          src={logoEafitNegro}
          alt="Logo de Eafit"
          className="w-8/12 object-contain"
        />

        <span
          className={`absolute -bottom-1 -right-1 h-5 w-5 rounded-full border-2 border-indigo-50 ${
            isError ? 'bg-red-500' : 'bg-green-500'
          }`}
        />

        {isError && (
          <span className="absolute left-full top-full ml-2 mt-0.5 whitespace-nowrap text-xs font-medium text-red-500 -translate-x-52">
            ¡Oh no! No se pudo conectar al backend
          </span>
        )}
      </div>

      <h1 className="mt-5 text-4xl font-semibold max-sm:text-3xl">
        Hola, soy el Asistente EAFIT
      </h1>

      <h2 className="w-100 text-lg max-sm:text-base">
        Tu guía de trámites, procesos y servicios de la Universidad EAFIT. ¿En
        qué puedo ayudarte hoy?
      </h2>
    </header>
  );
}
