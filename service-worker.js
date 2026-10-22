// NicheIQ GitHub Pages static app shell. Paths are relative to the repository site.
const CACHE_PREFIX = 'nicheiq-github-pages-';
const CACHE_NAME = CACHE_PREFIX + 'v2.0.0';
const APP_SHELL = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png'];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME)
    .then(cache => cache.addAll(APP_SHELL))
    .then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys()
    .then(keys => Promise.all(keys
      .filter(key => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME)
      .map(key => caches.delete(key))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;

  // Network-first for public research JSON. Cache last successful report offline.
  if (url.pathname.endsWith('/data/latest.json')) {
    event.respondWith(fetch(request).then(response => {
      if (response.ok) {
        const copy = response.clone();
        event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.put(request, copy)));
      }
      return response;
    }).catch(() => caches.match(request)));
    return;
  }

  // Use network-first for page navigation, so a new deployment is visible online.
  if (request.mode === 'navigate') {
    event.respondWith(fetch(request)
      .then(response => {
        if (response.ok) {
          const clone = response.clone();
          event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.put(request, clone)));
        }
        return response;
      })
      .catch(() => caches.match(request).then(hit => hit || caches.match('./index.html'))));
    return;
  }

  // Cache-first for the icons and manifest; only cache requests in this app's scope.
  if (!url.pathname.startsWith(new URL(self.registration.scope).pathname)) return;
  event.respondWith(caches.match(request)
    .then(hit => hit || fetch(request).then(response => {
      if (response.ok) {
        const clone = response.clone();
        event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.put(request, clone)));
      }
      return response;
    })));
});
