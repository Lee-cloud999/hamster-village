// 햄스터 마을 service worker: network-first so new versions show up right away; cache is the offline fallback.
const CACHE='hamster-village-v5';
const KEEP=['hamster-bgm']; // BGM은 게임이 직접 버전별로 캐시해요
const CORE=['./','./index.html','./manifest.webmanifest','./bg/day.webp','./bg/wide.webp','./bg/walk.webp','./bg/walk_mid.webp','./bg/path.webp','./icons/bori.png','./icons/icon-192.png','./icons/icon-512.png','./icons/apple-touch-icon.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE&&KEEP.indexOf(k)<0).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET')return;
  const sameOrigin=new URL(r.url).origin===location.origin;
  const isFont=/fonts\.(googleapis|gstatic)\.com/.test(r.url);
  if(!sameOrigin&&!isFont)return;
  if(sameOrigin&&/\/bgm\//.test(new URL(r.url).pathname))return; // 진행률 표시를 위해 BGM은 게임이 직접 받아요
  const isPage=r.mode==='navigate'||/\/(index\.html)?$/.test(new URL(r.url).pathname);
  const req=isPage?new Request(r.url,{cache:'no-cache',credentials:'same-origin'}):r; // 화면 파일은 항상 새로 확인
  e.respondWith(fetch(req).then(res=>{if(res&&(res.ok||res.type==='opaque')){const cp=res.clone();caches.open(CACHE).then(c=>c.put(r,cp));}return res;}).catch(()=>caches.match(r).then(m=>m||caches.match('./index.html'))));
});
