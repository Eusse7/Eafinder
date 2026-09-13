import { useEffect, useState, type ReactNode } from 'react';

import Bottombar from './Bottombar/components/Bottombar';
import Sidebar from './Sidebar/components/Sidebar';
import Topbar from './Topbar/components/Topbar';
import { getInitialSidebarStatus } from '../utils/getInitialSidebarStatus';
import { onChatLimitToast } from './Sidebar/utils/showChatLimitToast';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarStatus, setSidebarStatus] = useState(getInitialSidebarStatus());
  const [showLimitToast, setShowLimitToast] = useState(false);

  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;

    const unsubscribe = onChatLimitToast(() => {
      setShowLimitToast(true);

      clearTimeout(timeoutId);

      timeoutId = setTimeout(() => {
        setShowLimitToast(false);
      }, 3000);
    });

    return () => {
      clearTimeout(timeoutId);
      unsubscribe();
    };
  }, []);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        sidebarStatus={sidebarStatus}
        setSidebarStatus={setSidebarStatus}
      />

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <Topbar
          sidebarStatus={sidebarStatus}
          setSidebarStatus={setSidebarStatus}
        />

        <main className="min-h-0 flex-1 overflow-y-auto">{children}</main>

        <div className="border-t border-gray-200 bg-indigo-50/80">
          {showLimitToast && (
            <div className="px-8 pt-3">
              <div className="mx-auto w-fit rounded-lg bg-red-600 px-4 py-2 text-sm text-white shadow-lg">
                Solo puedes tener un máximo de 5 chats a la vez.
              </div>
            </div>
          )}

          <Bottombar />
        </div>
      </div>
    </div>
  );
}
