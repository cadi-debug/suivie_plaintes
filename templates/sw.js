const CACHE_NAME = 'sgp-justice-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/login/',
    '/static/img/logo.png',
    'https://cdn.tailwindcss.com', // On cache le CSS externe
    'https://unpkg.com/htmx.org@1.9.6', // On cache HTMX
    'https://d3js.org/d3.v7.min.js' // On cache D3
];

// 1. Installation : On met en cache les fichiers statiques
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// 2. Activation : On nettoie les vieux caches si on change de version
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== CACHE_NAME) {
                    return caches.delete(key);
                }
            }));
        })
    );
});

// 3. Interception Réseau (Fetch)
// Stratégie : "Stale-While-Revalidate" (Sert le cache, puis met à jour en arrière-plan)
self.addEventListener('fetch', (event) => {
    // On ne cache pas les requêtes API dynamiques (HTMX search, Graph Data)
    if (event.request.url.includes('/api/') || event.request.url.includes('search')) {
        return;
    }

    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            const fetchPromise = fetch(event.request).then((networkResponse) => {
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, networkResponse.clone());
                });
                return networkResponse;
            });
            // Si on a le fichier en cache, on le rend tout de suite, sinon on attend le réseau
            return cachedResponse || fetchPromise;
        })
    );
});