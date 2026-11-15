// Goldfox performance check: how much work the app makes the phone do while it's open.
// Usage (from the repo folder):  node tools/perf-check.js [git-ref-to-compare] [seconds]
//   e.g. node tools/perf-check.js HEAD~1 20   -> compares the last commit with the current index.html
// Measures, on Home and the Event log with a running sleep + breastfeed and 60 log entries:
//   repaints, repaint time, style recalculations, layouts, script time, total processor time,
//   what the running animations change (should only be opacity/transform), and that memory stays flat.
const {chromium}=require('playwright');
const {execSync}=require('child_process');
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
const ref=process.argv[2],secs=+(process.argv[3]||20);
const files={now:path.join(root,'zz_perf_now.html')};
fs.copyFileSync(path.join(root,'index.html'),files.now);
if(ref){files[ref]=path.join(root,'zz_perf_ref.html');fs.writeFileSync(files[ref],execSync('git show '+ref+':index.html',{cwd:root}))}
const seed=()=>{const now=Date.now();localStorage.setItem('bl.me','Mama');localStorage.setItem('bl.set',JSON.stringify({intro:'off',fly:'off'}));
  const ev={n1:{cat:'nap',at:now-42*6e4,end:null,by:'Papa'},b4:{cat:'feeding',type:'breastfeed',at:now-5*6e4,end:null,first:'L',side:'R',segAt:now-2*6e4,l:3*6e4,r:0,by:'Mama'}};
  for(let i=0;i<60;i++)ev['x'+i]={cat:['diaper','feeding','pump'][i%3],kind:'wet',ml:90,type:'formula',at:now-(i+1)*50*6e4,by:'Papa'};
  localStorage.setItem('bl.local',JSON.stringify({events:ev,meta:{people:{names:['Mama','Papa']},baby:{name:'Violetta',born:'2026-10-10'}}}))};
(async()=>{
  const b=await chromium.launch();const rows=[];
  try{
    for(const [ver,file] of Object.entries(files)) for(const scr of ['home','log']){
      const ctx=await b.newContext({viewport:{width:390,height:844}});const p=await ctx.newPage();
      const errs=[];p.on('pageerror',e=>errs.push(e.message));
      await p.route(/gstatic|firebase/,r=>r.abort());await p.addInitScript(seed);
      await p.goto('file://'+file);await p.waitForTimeout(1500);
      if(scr==='log'){await p.click('#bar [data-v="log"]');await p.waitForTimeout(1500)}
      const cdp=await ctx.newCDPSession(p);await cdp.send('Performance.enable');
      const M=async()=>Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map(x=>[x.name,x.value]));
      const m0=await M();
      await b.startTracing(p,{categories:['devtools.timeline','disabled-by-default-devtools.timeline']});
      await p.waitForTimeout(secs*1000);
      const ev=JSON.parse((await b.stopTracing()).toString()).traceEvents.filter(e=>e.name==='Paint'&&e.ph==='X');
      const m1=await M();
      const anim=await p.evaluate(()=>document.getAnimations().filter(a=>a.animationName).map(a=>[...new Set(a.effect.getKeyframes().flatMap(k=>Object.keys(k).filter(x=>!['offset','easing','composite','computedOffset'].includes(x))))].join('+')));
      const heavy=anim.filter(x=>!/^(opacity|transform|opacity\+transform|transform\+opacity)$/.test(x));
      rows.push({version:ver,screen:scr,repaints:ev.length,repaintMs:Math.round(ev.reduce((a,e)=>a+e.dur,0)/1000),
        styleRecalcs:Math.round(m1.RecalcStyleCount-m0.RecalcStyleCount),layouts:Math.round(m1.LayoutCount-m0.LayoutCount),
        scriptMs:Math.round((m1.ScriptDuration-m0.ScriptDuration)*1000),cpuMs:Math.round((m1.TaskDuration-m0.TaskDuration)*1000),
        animations:anim.length,heavyAnimations:heavy.length?heavy.join(','):'none',errors:errs.length});
      await ctx.close();
    }
    // memory: switch screens 30 times; the node count after cleanup must not keep growing
    for(const [ver,file] of Object.entries(files)){
      const ctx=await b.newContext({viewport:{width:390,height:844}});const p=await ctx.newPage();
      await p.route(/gstatic|firebase/,r=>r.abort());await p.addInitScript(seed);await p.goto('file://'+file);await p.waitForTimeout(1200);
      const cdp=await ctx.newCDPSession(p);await cdp.send('Performance.enable');
      const nodes=async()=>{await cdp.send('HeapProfiler.collectGarbage');return (await cdp.send('Performance.getMetrics')).metrics.find(x=>x.name==='Nodes').value};
      const cyc=async n=>{for(let i=0;i<n;i++){await p.click('#bar [data-v="log"]');await p.waitForTimeout(120);await p.click('#bar [data-v="home"]');await p.waitForTimeout(120)}};
      await cyc(5);const a=await nodes();await cyc(25);const c=await nodes();
      rows.filter(r=>r.version===ver).forEach(r=>r.memory=(c-a>50?'GROWING ':'flat ')+a+'→'+c+' nodes');
      await ctx.close();
    }
  }finally{await b.close();Object.values(files).forEach(f=>{try{fs.unlinkSync(f)}catch(e){}})}
  console.table(rows);
  const bad=rows.filter(r=>r.version==='now'&&(r.heavyAnimations!=='none'||r.errors||/GROWING/.test(r.memory)||r.repaints>secs*5));
  console.log(bad.length?'⚠ Needs attention: '+bad.map(r=>r.screen).join(', '):'✓ Performance check passed');
  process.exitCode=bad.length?1:0;
})();
