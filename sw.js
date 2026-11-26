// Service worker: lets the installed app open offline and keeps pages fresh.
// Pages: network first (always the latest), falling back to the saved copy, then the offline page.
// Styles, scripts, images: served from the saved copy and refreshed in the background.
const VERSION = '535ac89c31';
const CORE = 'core-' + VERSION;
const RUNTIME = 'runtime-' + VERSION;
const CORE_FILES = [
  '/', '/index.html', '/writing.html', '/guides/index.html', '/cases.html', '/offline.html', '/app.html',
  '/style.css', '/site.js', '/gate.js', '/site.webmanifest',
  '/icons/icon-192.png', '/icons/icon-512.png', '/icons/favicon.svg', '/favicon.ico'
];
const MAX_RUNTIME = 200;

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CORE)
      .then((c) => Promise.all(CORE_FILES.map((u) => c.add(new Request(u, { cache: 'reload' })).catch(() => null))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CORE && k !== RUNTIME).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

async function trim(cacheName, max) {
  const c = await caches.open(cacheName);
  const keys = await c.keys();
  for (let i = 0; i < keys.length - max; i++) await c.delete(keys[i]);
}

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // fonts, analytics etc. go straight to the network

  if (req.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const fresh = await fetch(req);
        if (fresh.ok) {
          const c = await caches.open(RUNTIME);
          c.put(req, fresh.clone());
          trim(RUNTIME, MAX_RUNTIME);
        }
        return fresh;
      } catch (e) {
        const saved = await caches.match(req, { ignoreSearch: true });
        return saved || (await caches.match('/offline.html')) || Response.error();
      }
    })());
    return;
  }

  event.respondWith((async () => {
    const saved = await caches.match(req);
    const network = fetch(req).then(async (res) => {
      if (res.ok) {
        const c = await caches.open(RUNTIME);
        c.put(req, res.clone());
        trim(RUNTIME, MAX_RUNTIME);
      }
      return res;
    }).catch(() => null);
    if (saved) { event.waitUntil(network); return saved; }
    return (await network) || (await caches.match(req, { ignoreSearch: true })) || Response.error();
  })());
});
