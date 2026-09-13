import { X } from 'lucide-react';

import Chats from './Chats';
import Footer from './Footer';
import Header from './Header';
import NewConversationButton from './NewConversationButton';

interface SidebarProps {
  sidebarStatus: boolean;
  setSidebarStatus: React.Dispatch<React.SetStateAction<boolean>>;
}

export default function Sidebar({
  sidebarStatus,
  setSidebarStatus,
}: SidebarProps) {
  return (
    <>
      {sidebarStatus && (
        <div
          className="fixed inset-0 z-40 bg-black/20 sm:hidden"
          onClick={() => setSidebarStatus(false)}
        />
      )}

      <aside
        className={`fixed left-0 top-0 z-50 flex h-screen flex-col overflow-hidden border-r border-gray-200 bg-white transition-[width] duration-300 ease-in-out sm:static sm:z-auto ${
          sidebarStatus ? 'w-64' : 'w-0'
        }`}
      >
        <div className="absolute right-4 top-4 z-10 sm:hidden">
          <button
            type="button"
            onClick={() => setSidebarStatus(false)}
            className="flex h-7 w-7 cursor-pointer items-center justify-center rounded-full text-gray-800 hover:bg-gray-200 hover:text-black"
          >
            <X size={17} strokeWidth={1} />
          </button>
        </div>

        <div
          className={`flex min-h-0 flex-1 flex-col transition-opacity duration-150 ${
            sidebarStatus ? 'opacity-100 delay-150' : 'opacity-0 delay-0'
          }`}
        >
          <Header />
          <NewConversationButton />
          <Chats />
          <Footer />
        </div>
      </aside>
    </>
  );
}
