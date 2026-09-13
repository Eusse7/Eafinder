export type DashboardPage = 'welcome' | 'inside-chat';

export function getCurrentPage(page: DashboardPage) {
  switch (page) {
    case 'welcome':
      return 'welcome';

    case 'inside-chat':
      return 'inside-chat';

    default:
      return 'welcome';
  }
}