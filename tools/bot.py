import re, sys, json, time
from playwright.sync_api import sync_playwright

SP = '/tmp/claude-0/-home-claude/3238aa5f-f12a-5cda-94f1-ad7565b85027/scratchpad/'
SRC = __import__('os').path.join(__import__('os').path.dirname(__file__),'..','index.html')
TARGET_LV = int(sys.argv[1]) if len(sys.argv) > 1 else 12
MAX_STEPS = int(sys.argv[2]) if len(sys.argv) > 2 else 3000

HOOK = r"""
window.G={get st(){return st},set sel(v){sel=v},get sel(){return sel},get dSel(){return dSel},setD(id,k){dSel=id;dPick=k;},get dexTab(){return dexTab},setDex(t,p){dexTab=t;dexSel=p;},
 generate,act,tap,deliver,submitOrder,findMatches,sellItem,emptyCells,canMerge,isLocked,isGen,openStory,chapterState,claimable,claimMany,openBoxStep,collectXp,collectEn,useTg,useTool,
 buyDecor,SPOTS,spotOpen,owned,tickEnergy,save,refresh,renderBoard,renderOrders,renderDecor,renderDex,storTake,nextGoal,STORY,PET_ORDER,petNeed,PET_COND,PET_LV,GENPOS,KEYS,CH,genOpen,openChains,
 decoCount,chReq,inTut,closeSheet,openSheet,CUST,petName,GU,guLv,REGEN,MAXLV,isSpecial,ordTick,nextPet,storyReady,swapOrder,swapCost,openChain,zoneDone,curZone,N,XPMAX,ENMAX,newOrder,mkOrder,petReady};
"""

BOT = r"""
window.BOT=(function(){
 const L=[];const log=s=>L.push(s);
 let simMin=0;let stuckN=0;
 function needsMap(){const st=G.st;const m={};st.orders.forEach(o=>{if(o.state==='done')return;o.needs.forEach(n=>{if(!n.done)m[n.c+n.l]=(m[n.c+n.l]||0)+1;});});
  /* 보드에 이미 있는 재료는 빼요 */ for(let i=0;i<G.N;i++){const x=st.cells[i];if(x&&!G.isLocked(i)&&!G.isGen(i)&&m[x.c+x.l]){m[x.c+x.l]--;if(!m[x.c+x.l])delete m[x.c+x.l];}}return m;}
 function needLv(c){let mx=0;G.st.orders.forEach(o=>{if(o.state==='done')return;o.needs.forEach(n=>{if(!n.done&&n.c===c)mx=Math.max(mx,n.l);});});return mx;}
 function nextChain(){const np=G.nextPet();return np&&np.c?np.c:null;}
 function items(){const st=G.st,r=[];for(let i=0;i<G.N;i++){const x=st.cells[i];if(x&&!G.isLocked(i)&&!G.isGen(i))r.push([i,x]);}return r;}
 function closeAll(){['dex','decor','chain','pass','quest','shop','ebuy','prof','set','stor'].forEach(id=>{try{const e=document.getElementById(id);if(e&&!e.hidden)G.closeSheet(id);}catch(e){}});}
 function step(){
  const st=G.st;const t=st.tut;
  closeAll();
  const sheet=document.querySelector('.sheet:not([hidden])');
  if(sheet&&['confirm','reward','rw','lvup'].indexOf(sheet.id)>=0)return 'sheet:'+sheet.id;
  // tutorial
  if(t===14&&st.coins>=40){document.getElementById('navDecor').click();return 'tut14 decor';}
  if((t===15||t===16)&&st.coins>=40){G.setD('bed',0);G.buyDecor();closeAll();return 'tut buy bed';}
  if(t===17){closeAll();document.getElementById('navDex').click();return 'tut17 dex';}
  if(t===18){if(G.chapterState(0,0)!=='ready')return 'tut18 story-locked';G.setDex('res',0);G.renderDex();G.openStory(0,0);return 'tut18 story';}
  if(t===12){G.openChain('br',3);closeAll();return 'tut12 chain';}
  if(t===5||t===7){document.body.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}));return 'tut skip';}
  // specials
  for(const [i,x] of items()){
   if(x.c==='bx'){G.sel=null;G.openBoxStep(i);return 'box '+i;}
   if(x.c==='xp'){G.collectXp(i);return 'xp';}
   if(x.c==='en'&&st.e<20){G.collectEn(i);return 'energy item';}
   if(x.c==='tg'&&G.emptyCells().length>3){G.sel=null;G.useTg(i);return 'honey';}
  }
  // storage
  if(st.stor&&st.stor.length&&G.emptyCells().length>4){G.storTake(0);return 'storage take';}
  // deliver
  for(let k=0;k<st.orders.length;k++){const o=st.orders[k];if(o.state!=='done'&&G.findMatches(k).length&&G.findMatches(k).length>=o.needs.filter(n=>!n.done).length){G.submitOrder(k);return 'deliver '+G.petName(o.cu);}}
  // pass rewards
  if(!G.inTut()&&G.claimable().length){G.claimMany(G.claimable());return 'claim pass';}
  // stories
  if(!G.inTut())for(const p of st.unlocked){const k=st.read[p]||0;if(k<G.STORY[p].length&&G.chapterState(p,k)==='ready'){G.openStory(p,k);return 'story '+G.petName(p)+' '+(k+1);}}
  // decor
  if(!G.inTut()){const sp=G.SPOTS.filter(x=>G.spotOpen(x)&&st.coins>=x.cost+80).sort((a,b)=>a.cost-b.cost)[0];if(sp){G.setD(sp.id,0);G.buyDecor();closeAll();return 'decor '+sp.n;}}
  // merge
  const nm=needsMap(),its=items().filter(x=>!G.isSpecial(x[1].c)||x[1].c==='en'),empty=G.emptyCells().length;
  const tgt=c=>{let m=needLv(c);const nc=nextChain();if(nc===c)m=Math.max(m,G.MAXLV);if((st.fmax[c]||0)<G.MAXLV&&G.genOpen(c))m=Math.max(m,Math.min(G.MAXLV,(st.fmax[c]||1)+1));return m;};
  let best=null,bs=-1;
  for(let a=0;a<its.length;a++)for(let b=a+1;b<its.length;b++){const [i,x]=its[a],[j,y]=its[b];if(!G.canMerge(i,j))continue;
   const key=x.c+x.l;const cnt=its.filter(z=>z[1].c===x.c&&z[1].l===x.l).length;
   if(nm[key]&&cnt-2<nm[key]&&x.l+1>tgt(x.c))continue; // keep needed ones
   let s=0;if(nm[x.c+(x.l+1)])s=100;else if(x.l+1<=tgt(x.c))s=50-x.l;else if(empty<4)s=5-x.l;else continue;
   if(nm[key]&&cnt-2<nm[key])s-=30;
   if(s>bs){bs=s;best=[i,j];}}
  if(best){G.sel=null;G.act(best[0],best[1]);return 'merge '+its.find(z=>z[0]===best[0])[1].c+its.find(z=>z[0]===best[0])[1].l;}
  // tools: use tool on lowest item
  for(const [i,x] of items()){if(x.c==='tl'){const tg=items().filter(z=>!G.isSpecial(z[1].c)).sort((a,b)=>b[1].l-a[1].l)[0];if(tg){G.sel=null;G.act(i,tg[0]);return 'tool';}}}
  // orders: swap impossible ones (chain not open)
  for(let k=0;k<st.orders.length;k++){const o=st.orders[k];if(o.state==='done')continue;if(o.needs.some(n=>!n.done&&!G.genOpen(n.c))&&st.coins>=G.swapCost()*3){G.swapOrder(k);return 'swap-request '+G.petName(o.cu);}}
  // generate
  G.tickEnergy();
  if(empty<=1){const sell=its.filter(z=>!G.isSpecial(z[1].c)&&!(nm[z[1].c+z[1].l])).sort((a,b)=>a[1].l-b[1].l)[0];if(sell){G.sel=null;G.sellItem(sell[0]);return 'sell '+sell[1].c+sell[1].l;}return 'board full';}
  if(st.e<1){
   if(!st.orders.some(o=>o.state!=='done')){st.oNext=Date.now()-1;G.ordTick();return 'orders refill';}
   const k=20;st.eAt-=G.REGEN*k;G.tickEnergy();simMin+=k*2;log('⏳ 에너지 0 → '+(k*2)+'분 기다림 (누적 '+simMin+'분, Lv'+st.lv+')');return 'wait';}
  // chain choice
  const chains=G.openChains();let pick=null,ps=-1;
  for(const c of chains){let s=0;Object.keys(nm).forEach(k=>{if(k.slice(0,2)===c)s+=nm[k]*(parseInt(k.slice(2))+1);});if(nextChain()===c&&(st.fmax[c]||0)<G.MAXLV)s+=3;if(c==='br')s+=0.5;if(s>ps){ps=s;pick=c;}}
  if(!pick)pick='br';
  const before=st.e;G.generate(pick);
  if(st.e===before&&G.emptyCells().length===empty){stuckN++;if(stuckN>5){st.oNext=Date.now()-1;G.ordTick();stuckN=0;return 'nudge orders';}return 'gen-noop';}
  stuckN=0;return 'gen '+pick;
 }
 return {step,log:L,get simMin(){return simMin}};
})();
"""

def main():
    html = open(SRC, encoding='utf-8').read()
    # inject hook before the IIFE close of the big script
    i = html.rfind("})();", 0, html.find("if('serviceWorker'"))
    html = html[:i] + HOOK + html[i:]
    html = html.replace("if('serviceWorker' in navigator)", "if(false)")
    html = html.replace("</body>", "<script>" + BOT + "</script></body>")
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 412, 'height': 800})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=html))
        pg.goto('http://localhost:8766/index.html'); pg.wait_for_timeout(2500)
        pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_timeout(2500)
        stb = pg.get_by_text('시작하기').first
        if stb.is_visible(): stb.click(force=True)
        pg.wait_for_timeout(1500)
        LOG=open(SP+'bot.log','w'); timeline = []; last = {}
        def tl(x):
            timeline.append(x); LOG.write(x+'\n'); LOG.flush()
        def dismiss():
            for _ in range(40):
                bs = [x for x in pg.locator('.sheet:not([hidden]) button').all() if x.is_visible() and x.evaluate("e=>{const s=e.closest('.sheet');if(['dex','decor','chain','quest','shop','ebuy','prof','set','stor','dev'].indexOf(s.id)>=0)return false;const t=e.textContent.trim();return e.id==='rwOk'||e.id==='cOk'||e.classList.contains('main')||/^(확인|좋아요|받기|다음|닫기)/.test(t);}")]
                if not bs: break
                if _>12: tl('  (dismiss loop) '+bs[0].evaluate('e=>e.closest(".sheet").id+" "+e.textContent.trim()'))
                try:
                    tt = pg.evaluate("(()=>{const e=document.querySelector('.sheet:not([hidden]) #rwT');return e?e.textContent:''})()")
                    if tt and tt not in last: last[tt]=1; tl(f"  💬 팝업: {tt}")
                except Exception: pass
                bs[0].click(force=True); pg.wait_for_timeout(200)
        steps = 0; t0 = time.time(); prevlv = 1; prevunl = 1; hist = []
        while steps < MAX_STEPS:
            steps += 1
            try:
                r = pg.evaluate("BOT.step()")
            except Exception as e:
                tl(f"ERR {e}"); break
            hist.append(r); LOG.write('    '+r+'\n'); LOG.flush()
            pg.wait_for_timeout(60 if r.startswith(('merge','gen','wait')) else 500)
            dismiss()
            s = pg.evaluate("(()=>{const st=G.st;return {lv:st.lv,xp:st.xp,e:st.e,coins:st.coins,unl:st.unlocked.length,read:JSON.stringify(st.read),tut:st.tut,orders:st.orders.filter(o=>o.state!=='done').map(o=>G.petName(o.cu)+':'+o.needs.map(n=>(n.done?'✓':'')+n.c+n.l).join(',')),goal:(G.nextGoal()||{}).t,fmax:JSON.stringify(st.fmax||{}),dec:Object.keys(st.dec||{}).length,hb:JSON.stringify(st.hlv||{}),fog:(st.fogOpen||[]).length}})()")
            if s['lv'] != prevlv:
                tl(f"[{steps}] ⬆ Lv{s['lv']} (코인 {s['coins']}, 장식 {s['dec']}, 읽은 이야기 {s['read']}, 기다린 시간 {pg.evaluate('BOT.simMin')}분)"); prevlv = s['lv']
            if s['unl'] != prevunl:
                tl(f"[{steps}] 🐹 새 이웃! 주민 {s['unl']}명 (Lv{s['lv']})"); prevunl = s['unl']
            lg = pg.evaluate("BOT.log.splice(0)")
            for x in lg: tl(f"[{steps}] {x}")
            if steps % 100 == 0:
                tl('    dbg '+pg.evaluate("JSON.stringify({chains:G.openChains(),gOpen:G.st.gOpen,e:G.st.e,nextPet:G.nextPet()})"))
                tl(f"[{steps}] 상태 Lv{s['lv']} xp{s['xp']} e{s['e']} 코인{s['coins']} 주민{s['unl']} 부탁{s['orders']} 목표:{s['goal']} fmax{s['fmax']} 선물{s['hb']} 안개{s['fog']}")
            if len(hist) > 60 and len(set(hist[-60:])) <= 2:
                tl(f"[{steps}] ⚠ 막힘: 최근 행동 {set(hist[-60:])} · 부탁 {s['orders']} · 목표 {s['goal']} · e{s['e']} 코인{s['coins']}")
                hist = []
                pg.screenshot(path=SP + f'stuck{steps}.png')
            if s['lv'] >= TARGET_LV: tl(f"[{steps}] 🎯 목표 레벨 도달"); break
            if pg.evaluate("!!G.st.s1"): tl(f"[{steps}] 🏁 시즌1 종료 (Lv{s['lv']}, 기다린 시간 {pg.evaluate('BOT.simMin')}분)"); break
        pg.screenshot(path=SP + 'bot_end.png')
        print('\n'.join(timeline)); print('errors:', errs[:5]); print('steps', steps, 'real sec', round(time.time()-t0))
main()
