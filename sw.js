/* ENDURACE LAB · service worker.
   Estrategia "red primero": siempre sirve la versión más reciente y, si no hay conexión,
   usa la copia guardada. Así las calculadoras funcionan sin cobertura el día de la carrera. */
const CACHE = "endurace-v3";
const CORE = ["./", "index.html", "laboratorio.html", "running.html", "test.html", "blog.html",
  "calculadora-ritmo-maraton.html", "calculadora-zonas-entrenamiento.html", "calculadora-nutricion-carrera.html", "cuenta-atras-carrera.html",
  "style.css?v=5", "lab.css?v=6", "fx.js", "calc.js?v=1", "temporada.js?v=1", "pagos.js", "logo.svg", "posts.json"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE)
    .then(c => Promise.all(CORE.map(u => c.add(u).catch(() => {}))))
    .then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const r = e.request;
  if (r.method !== "GET" || new URL(r.url).origin !== location.origin) return;
  e.respondWith(
    fetch(r).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(r, copy)); }
      return res;
    }).catch(() => caches.match(r).then(m => m || caches.match(r, {ignoreSearch: true})))
  );
});
