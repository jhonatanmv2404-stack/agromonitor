const CACHE_NAME = 'agromonitor-v5.2';
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME));
});
self.addEventListener('fetch', e => {
  e.respondWith(fetch(e.request));
});
