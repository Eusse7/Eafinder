import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

import Dashboard from './dashboard/components/Dashboard';
import InsideChat from './dashboard/pages/2-inside-chat/components/InsideChat';
import Layout from './layout/components/Layout';

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat/:chatId" element={<InsideChat />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
