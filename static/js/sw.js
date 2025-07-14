/**
 * ChatMoji Service Worker
 * Provides offline functionality and performance optimization
 */

const CACHE_NAME = 'chatmoji-v1.0.0';
const STATIC_CACHE = 'chatmoji-static-v1.0.0';
const DYNAMIC_CACHE = 'chatmoji-dynamic-v1.0.0';

// Files to cache immediately
const STATIC_FILES = [
    '/',
    '/static/css/main.css',
    '/static/js/emoji-converter.js',
    '/static/js/main.js',
    'https://cdn.tailwindcss.com',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

// Dynamic content to cache
const DYNAMIC_FILES = [
    '/chat/dashboard/',
    '/accounts/friends/',
    '/accounts/profile/'
];

// Files that should always be fetched from network
const NETWORK_FIRST = [
    '/chat/api/',
    '/accounts/api/',
    '/ws/'
];

/**
 * Install event - cache static files
 */
self.addEventListener('install', event => {
    console.log('ChatMoji Service Worker: Installing...');
    
    event.waitUntil(
        Promise.all([
            caches.open(STATIC_CACHE).then(cache => {
                console.log('ChatMoji Service Worker: Caching static files');
                return cache.addAll(STATIC_FILES);
            }),
            caches.open(DYNAMIC_CACHE).then(cache => {
                console.log('ChatMoji Service Worker: Initializing dynamic cache');
                return Promise.resolve();
            })
        ]).then(() => {
            console.log('ChatMoji Service Worker: Installation complete');
            return self.skipWaiting();
        })
    );
});

/**
 * Activate event - clean up old caches
 */
self.addEventListener('activate', event => {
    console.log('ChatMoji Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                        console.log('ChatMoji Service Worker: Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('ChatMoji Service Worker: Activation complete');
            return self.clients.claim();
        })
    );
});

/**
 * Fetch event - handle requests with different strategies
 */
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip WebSocket requests
    if (url.protocol === 'ws:' || url.protocol === 'wss:') {
        return;
    }
    
    // Handle different types of requests
    if (isStaticFile(request.url)) {
        event.respondWith(handleStaticFile(request));
    } else if (isNetworkFirst(request.url)) {
        event.respondWith(handleNetworkFirst(request));
    } else if (isDynamicContent(request.url)) {
        event.respondWith(handleDynamicContent(request));
    } else {
        event.respondWith(handleDefault(request));
    }
});

/**
 * Check if file is a static asset
 */
function isStaticFile(url) {
    return STATIC_FILES.some(staticFile => url.includes(staticFile)) ||
           url.includes('/static/') ||
           url.includes('cdn.tailwindcss.com') ||
           url.includes('cdnjs.cloudflare.com');
}

/**
 * Check if request should use network-first strategy
 */
function isNetworkFirst(url) {
    return NETWORK_FIRST.some(pattern => url.includes(pattern));
}

/**
 * Check if content is dynamic
 */
function isDynamicContent(url) {
    return DYNAMIC_FILES.some(pattern => url.includes(pattern)) ||
           url.includes('/chat/') ||
           url.includes('/accounts/');
}

/**
 * Handle static files - cache first strategy
 */
async function handleStaticFile(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        const cache = await caches.open(STATIC_CACHE);
        cache.put(request, networkResponse.clone());
        
        return networkResponse;
    } catch (error) {
        console.error('ChatMoji Service Worker: Static file error:', error);
        return new Response('Offline - Static file unavailable', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

/**
 * Handle network-first requests (API calls)
 */
async function handleNetworkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        
        // Cache successful responses
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.log('ChatMoji Service Worker: Network error, trying cache:', error);
        
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        return new Response(JSON.stringify({
            error: 'Offline - Network unavailable',
            offline: true
        }), {
            status: 503,
            statusText: 'Service Unavailable',
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

/**
 * Handle dynamic content - network first, cache fallback
 */
async function handleDynamicContent(request) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page for navigation requests
        if (request.mode === 'navigate') {
            return caches.match('/') || new Response(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>ChatMoji - Offline</title>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            min-height: 100vh;
                            margin: 0;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            text-align: center;
                        }
                        .offline-container {
                            max-width: 400px;
                            padding: 2rem;
                        }
                        .emoji {
                            font-size: 4rem;
                            margin-bottom: 1rem;
                        }
                        h1 { margin-bottom: 1rem; }
                        p { margin-bottom: 2rem; opacity: 0.9; }
                        button {
                            background: rgba(255,255,255,0.2);
                            border: 2px solid white;
                            color: white;
                            padding: 12px 24px;
                            border-radius: 25px;
                            cursor: pointer;
                            font-size: 1rem;
                        }
                        button:hover {
                            background: rgba(255,255,255,0.3);
                        }
                    </style>
                </head>
                <body>
                    <div class="offline-container">
                        <div class="emoji">📡</div>
                        <h1>You're Offline</h1>
                        <p>ChatMoji needs an internet connection. Check your connection and try again.</p>
                        <button onclick="window.location.reload()">Try Again</button>
                    </div>
                </body>
                </html>
            `, {
                headers: { 'Content-Type': 'text/html' }
            });
        }
        
        return new Response('Offline', { status: 503 });
    }
}

/**
 * Default handler for other requests
 */
async function handleDefault(request) {
    try {
        return await fetch(request);
    } catch (error) {
        const cachedResponse = await caches.match(request);
        return cachedResponse || new Response('Offline', { status: 503 });
    }
}

/**
 * Background sync for offline actions
 */
self.addEventListener('sync', event => {
    console.log('ChatMoji Service Worker: Background sync triggered');
    
    if (event.tag === 'emoji-conversion-sync') {
        event.waitUntil(syncEmojiConversions());
    } else if (event.tag === 'message-sync') {
        event.waitUntil(syncMessages());
    }
});

/**
 * Sync emoji conversions when back online
 */
async function syncEmojiConversions() {
    try {
        console.log('ChatMoji Service Worker: Syncing emoji conversions');
        
        // Get pending conversions from IndexedDB
        const pendingConversions = await getPendingConversions();
        
        for (const conversion of pendingConversions) {
            try {
                // Process conversion
                await fetch('/api/emoji-conversion/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(conversion)
                });
                
                // Remove from pending
                await removePendingConversion(conversion.id);
            } catch (error) {
                console.error('Failed to sync conversion:', error);
            }
        }
    } catch (error) {
        console.error('ChatMoji Service Worker: Sync error:', error);
    }
}

/**
 * Sync messages when back online
 */
async function syncMessages() {
    try {
        console.log('ChatMoji Service Worker: Syncing messages');
        
        // Get pending messages from IndexedDB
        const pendingMessages = await getPendingMessages();
        
        for (const message of pendingMessages) {
            try {
                // Send message
                await fetch('/chat/api/send-message/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(message)
                });
                
                // Remove from pending
                await removePendingMessage(message.id);
            } catch (error) {
                console.error('Failed to sync message:', error);
            }
        }
    } catch (error) {
        console.error('ChatMoji Service Worker: Message sync error:', error);
    }
}

/**
 * Push notification handler
 */
self.addEventListener('push', event => {
    console.log('ChatMoji Service Worker: Push received');
    
    const options = {
        body: 'You have a new message!',
        icon: '/static/images/icon-192.png',
        badge: '/static/images/badge-72.png',
        tag: 'chatmoji-message',
        data: {
            url: '/chat/dashboard/'
        },
        actions: [
            {
                action: 'view',
                title: 'View Message',
                icon: '/static/images/view-icon.png'
            },
            {
                action: 'dismiss',
                title: 'Dismiss',
                icon: '/static/images/dismiss-icon.png'
            }
        ]
    };
    
    if (event.data) {
        const data = event.data.json();
        options.body = data.message || options.body;
        options.data.conversationId = data.conversationId;
    }
    
    event.waitUntil(
        self.registration.showNotification('ChatMoji', options)
    );
});

/**
 * Notification click handler
 */
self.addEventListener('notificationclick', event => {
    console.log('ChatMoji Service Worker: Notification clicked');
    
    event.notification.close();
    
    const { action, data } = event;
    
    if (action === 'view' || !action) {
        const url = data.conversationId ? 
            `/chat/conversation/${data.conversationId}/` : 
            data.url || '/chat/dashboard/';
        
        event.waitUntil(
            clients.matchAll({ type: 'window' }).then(clientList => {
                // Check if ChatMoji is already open
                for (const client of clientList) {
                    if (client.url.includes('chatmoji') && 'focus' in client) {
                        client.navigate(url);
                        return client.focus();
                    }
                }
                
                // Open new window
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
        );
    }
});

/**
 * Message handler for client communication
 */
self.addEventListener('message', event => {
    console.log('ChatMoji Service Worker: Message received from client');
    
    const { type, data } = event.data;
    
    switch (type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;
            
        case 'GET_CACHE_STATUS':
            event.ports[0].postMessage({
                staticCacheSize: 0, // Will be calculated
                dynamicCacheSize: 0
            });
            break;
            
        case 'CLEAR_CACHE':
            clearAllCaches().then(() => {
                event.ports[0].postMessage({ success: true });
            });
            break;
            
        case 'STORE_OFFLINE_DATA':
            storeOfflineData(data).then(() => {
                event.ports[0].postMessage({ success: true });
            });
            break;
    }
});

/**
 * Utility functions for IndexedDB operations
 */
async function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('ChatMojiDB', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            if (!db.objectStoreNames.contains('pendingConversions')) {
                db.createObjectStore('pendingConversions', { keyPath: 'id' });
            }
            
            if (!db.objectStoreNames.contains('pendingMessages')) {
                db.createObjectStore('pendingMessages', { keyPath: 'id' });
            }
            
            if (!db.objectStoreNames.contains('offlineData')) {
                db.createObjectStore('offlineData', { keyPath: 'key' });
            }
        };
    });
}

async function getPendingConversions() {
    const db = await openDB();
    const transaction = db.transaction(['pendingConversions'], 'readonly');
    const store = transaction.objectStore('pendingConversions');
    
    return new Promise((resolve, reject) => {
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function getPendingMessages() {
    const db = await openDB();
    const transaction = db.transaction(['pendingMessages'], 'readonly');
    const store = transaction.objectStore('pendingMessages');
    
    return new Promise((resolve, reject) => {
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function removePendingConversion(id) {
    const db = await openDB();
    const transaction = db.transaction(['pendingConversions'], 'readwrite');
    const store = transaction.objectStore('pendingConversions');
    
    return new Promise((resolve, reject) => {
        const request = store.delete(id);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

async function removePendingMessage(id) {
    const db = await openDB();
    const transaction = db.transaction(['pendingMessages'], 'readwrite');
    const store = transaction.objectStore('pendingMessages');
    
    return new Promise((resolve, reject) => {
        const request = store.delete(id);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

async function storeOfflineData(data) {
    const db = await openDB();
    const transaction = db.transaction(['offlineData'], 'readwrite');
    const store = transaction.objectStore('offlineData');
    
    return new Promise((resolve, reject) => {
        const request = store.put(data);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

async function clearAllCaches() {
    const cacheNames = await caches.keys();
    return Promise.all(
        cacheNames.map(cacheName => caches.delete(cacheName))
    );
}

console.log('ChatMoji Service Worker: Loaded successfully');