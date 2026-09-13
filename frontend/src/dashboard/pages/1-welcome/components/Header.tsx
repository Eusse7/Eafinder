import logoEafitNegro from '../assets/logoEafitNegro.jpg';

export default function Header() {
  return (
    <header className="flex h-full w-full flex-col items-center gap-3 text-center">
      <div className="relative mt-5 flex h-20 w-44 justify-center rounded-2xl bg-white shadow-[0_0_20px_rgba(0,0,0,0.2)]">
        <img
          src={logoEafitNegro}
          alt="Logo de Eafit"
          className="w-8/12 object-contain"
        />

        <span className="absolute -bottom-1 -right-1 h-5 w-5 rounded-full border-2 border-indigo-50 bg-green-500" />
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
