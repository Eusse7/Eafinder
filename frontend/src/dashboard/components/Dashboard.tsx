import { useState } from 'react';

import { getCurrentPage, type DashboardPage } from '../utils/getCurrentPage';
import Welcome from '../pages/1-welcome/components/Welcome';
import InsideChat from '../pages/2-inside-chat/components/InsideChat';

export default function Dashboard() {
  const [page, setPage] = useState<DashboardPage>('welcome');

  const currentPage = getCurrentPage(page);

  return (
    <div className="h-full w-full overflow-x-hidden bg-indigo-50/80">
      {currentPage === 'welcome' && <Welcome />}
      {currentPage === 'inside-chat' && <InsideChat />}
    </div>
  );
}
