import { Routes } from '@angular/router';

import { ChatPage } from './pages/chat/chat.page';
import { WelcomePage } from './pages/welcome/welcome.page';

export const routes: Routes = [
  { path: '', component: WelcomePage },
  { path: 'chat/:chatId', component: ChatPage },
  { path: '**', redirectTo: '' },
];
