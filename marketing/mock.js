// Stubs the WebExtension API so the REAL popup/options pages render with sample data.
(() => {
  if (!location.pathname.includes('/extension/pages/')) return;
  const q = new URLSearchParams(location.search);
  const store = { limit: +(q.get('limit') || 3), scope: 'all', mode: 'block', enabled: true, checkUpdates: true,
    blocked: +(q.get('blocked') || 127), blockedToday: +(q.get('today') || 9),
    blockedDay: new Date().toISOString().slice(0, 10), updateAvailable: '' };
  const n = +(q.get('tabs') || 3);
  Object.defineProperty(window, 'chrome', { value: {
    storage: { local: { get: async d => ({ ...d, ...store }), set: async o => Object.assign(store, o) } },
    windows: { getCurrent: async () => ({ id: 1 }) }, tabs: { query: async () => Array(n).fill({}) },
    runtime: { openOptionsPage() {}, getManifest: () => ({ version: '1.0.0' }) } } });
})();
