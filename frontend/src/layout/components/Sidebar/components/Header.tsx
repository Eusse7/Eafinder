import logoEafitNegro from '../assets/logoEafitNegro.jpg';

export default function Header() {
  return (
    <div className="flex flex-col border-b border-gray-200 items-center pb-4 pt-4">
      <img
        className="w-1/3 opacity-50"
        src={logoEafitNegro}
        alt="Logo de Eafit"
      />
      <p className="text-xs text-gray-500">Asistente Universitario</p>
    </div>
  );
}
