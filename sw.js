// This site moved to https://custoslaw.github.io - clear the old offline copy.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil((async () => {
  for (const k of await caches.keys()) await caches.delete(k);
  await self.registration.unregister();
  for (const c of await self.clients.matchAll({type: 'window'})) {
    const u = new URL(c.url); c.navigate('https://custoslaw.github.io' + u.pathname + u.search + u.hash);
  }
})()));
