/* Free Constitution offline support. Caches pages you open on this device only. */
const V = "fc-20261001b";
const CORE = ["/", "/situations/", "/offline/", "/static/css/site.css?v=20261001b", "/static/js/app.js?v=20261001b", "/static/fonts/atkinson-hyperlegible-next-latin-400-normal.woff2", "/static/fonts/atkinson-hyperlegible-next-latin-700-normal.woff2", "/static/favicon.svg", "/situations/being-questioned-by-police/", "/situations/searched-by-police/", "/situations/at-school/", "/situations/posting-online/", "/situations/at-work/", "/situations/recording-police/", "/situations/first-time-voter/", "/situations/at-a-protest/", "/situations/turned-away-from-voting/", "/situations/immigration-agents-at-the-door/"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const r = e.request;
  if (r.method !== "GET" || new URL(r.url).origin !== location.origin) return;
  if (r.mode === "navigate") {
    e.respondWith(fetch(r).then(res => { const copy = res.clone(); caches.open(V).then(c => c.put(r, copy)); return res; })
      .catch(() => caches.match(r).then(m => m || caches.match("/offline/"))));
    return;
  }
  e.respondWith(caches.match(r).then(m => m || fetch(r).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(V).then(c => c.put(r, copy)); }
    return res;
  })));
});
