import { Routes } from '@angular/router';

import { AnalyticsPage } from './pages/analytics/analytics.page';
import { ChatPage } from './pages/chat/chat.page';
import { WelcomePage } from './pages/welcome/welcome.page';

export const routes: Routes = [
  { path: '', component: WelcomePage },
  { path: 'analytics', component: AnalyticsPage },
  { path: 'chat/:chatId', component: ChatPage },
  { path: '**', redirectTo: '' },
];
