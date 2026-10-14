// 햄스터 마을 service worker: network-first so new versions show up right away; cache is the offline fallback.
const CACHE='hamster-village-v2';
const CORE=['./','./index.html','./manifest.webmanifest','./bg/day.webp','./bg/wide.webp','./icons/bori.png','./icons/icon-192.png','./icons/icon-512.png','./icons/apple-touch-icon.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET')return;
  const sameOrigin=new URL(r.url).origin===location.origin;
  const isFont=/fonts\.(googleapis|gstatic)\.com/.test(r.url);
  if(!sameOrigin&&!isFont)return;
  e.respondWith(fetch(r).then(res=>{if(res&&(res.ok||res.type==='opaque')){const cp=res.clone();caches.open(CACHE).then(c=>c.put(r,cp));}return res;}).catch(()=>caches.match(r).then(m=>m||caches.match('./index.html'))));
});
