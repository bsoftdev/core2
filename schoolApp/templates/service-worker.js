
const CACHE_NAME = "django-pwa-static-v1";

const STATIC_ASSETS = [
  "/static/pwa/offline.html",
  "/static/pwa/icons/icon-192.png",
  "/static/pwa/icons/icon-512.png"
];

// Instalação: guarda apenas recursos estáticos.
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );

  self.skipWaiting();
});

// Ativação: remove caches antigos desta aplicação.
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys
          .filter((key) =>
            key.startsWith("django-pwa-static-") &&
            key !== CACHE_NAME
          )
          .map((key) => caches.delete(key))
      );
    })
  );

  self.clients.claim();
});

// Interceta apenas pedidos GET do mesmo domínio.
self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);

  if (
    request.method !== "GET" ||
    url.origin !== self.location.origin
  ) {
    return;
  }

  // Páginas dinâmicas: sempre tentar contactar o servidor.
  // Nunca guardar páginas privadas ou autenticadas.
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).catch(async () => {
        const offlinePage = await caches.match(
          "/static/pwa/offline.html"
        );

        if (offlinePage) {
          return offlinePage;
        }

        return new Response(
          "Sem ligação à Internet. Tenta novamente.",
          {
            status: 503,
            headers: {
              "Content-Type": "text/plain; charset=utf-8"
            }
          }
        );
      })
    );

    return;
  }

  // Cache apenas os recursos da pasta da PWA.
  if (url.pathname.startsWith("/static/pwa/")) {
    event.respondWith(
      caches.match(request).then(async (cached) => {
        if (cached) {
          return cached;
        }

        const response = await fetch(request);

        if (response.ok && response.type === "basic") {
          const cache = await caches.open(CACHE_NAME);
          await cache.put(request, response.clone());
        }

        return response;
      })
    );
  }
});
