export function getInitialSidebarStatus() {
  return window.matchMedia('(min-width: 640px)').matches;
}