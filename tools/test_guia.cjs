const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'GUIASUPERDETALLADA.html'),'utf8');
const extract=id=>html.match(new RegExp('<script id="'+id+'">([\\s\\S]*?)</script>'))[1];
const ctx=vm.createContext({});
vm.runInContext(extract('guide-content')+'\n'+extract('guide-state')+'\nthis.exports={guideSteps,freshState,validateState,stepDone,completedCount,firstPending};',ctx);
const g=ctx.exports;
for(const os of ['windows','mac']) {
 const steps=g.guideSteps(os);assert.equal(steps.length,15);assert.equal(new Set(steps.map(s=>s.id)).size,15);
 for(const s of steps){assert.ok(s.html.length>100);assert.ok(s.checks.length>0);assert.ok(s.title);}
 const fresh=g.freshState();assert.equal(g.completedCount(fresh.paths[os],steps),0);
 fresh.activeOS=os;fresh.paths[os].checks.welcome=[true,true];fresh.paths[os].notes.welcome='Árboles <script>literal</script>';
 const restored=g.validateState(JSON.parse(JSON.stringify(fresh)));
 assert.equal(g.completedCount(restored.paths[os],steps),1);assert.equal(g.firstPending(restored.paths[os],steps),'folder');
 assert.equal(g.completedCount(restored.paths[os==='mac'?'windows':'mac'],steps),0);
 assert.equal(restored.paths[os].notes.welcome,'Árboles <script>literal</script>');
 const bad=JSON.parse(JSON.stringify(fresh));bad.paths[os].checks.welcome=['true',true];assert.throws(()=>g.validateState(bad));
 bad.paths[os].checks.welcome=[true,true];bad.paths[os].notes.welcome='x'.repeat(3001);assert.throws(()=>g.validateState(bad));
}
assert.throws(()=>g.validateState({version:1}));
assert.equal(html.includes('https://fonts.googleapis.com'),false);
const canonical=fs.readFileSync(path.join(root,'proyecto/Framework-Edicion-Social/FLUJO_PRODUCCION_RAPIDA.md'),'utf8');
const recording=fs.readFileSync(path.join(root,'GUIA_GRABACION_MASTER.html'),'utf8');
for(const marker of ['MARCADOR. Video N, toma N, inicio.','MARCADOR. Corregir, corregir. Última frase.','MARCADOR. Aprobada, aprobada.','MARCADOR. Descartar, descartar.','MARCADOR. Fin de sesión.']){assert.ok(canonical.includes(marker));assert.ok(recording.includes(marker));}
async function storageContract(){
 let rev=0,disk=null,offline=false;const states=[];
 const clientContext=vm.createContext({JSON,Date,Error,TypeError,AbortController,setTimeout,clearTimeout,location:{hash:'#test'},fetch:async(_url,options)=>{
  if(offline)throw new TypeError('offline');
  if(options.method==='GET')return {ok:true,json:async()=>({revision:rev,data:disk})};
  const request=JSON.parse(options.body);
  if(request.revision!==rev)return {ok:false,json:async()=>({error:'conflict'})};
  disk=request.data;rev++;return {ok:true,json:async()=>({saved:true,revision:rev})};
 }});
 vm.runInContext(fs.readFileSync(path.join(root,'asistente/progreso.js'),'utf8')+'\nthis.Client=FolderProgress;',clientContext);
 const a=new clientContext.Client('guia',(status)=>states.push(status));await a.load();
 a.queue({note:'mañana'});assert.equal(a.dirty,true);await a.flush();assert.equal(a.dirty,false);assert.equal(disk.note,'mañana');
 const b=new clientContext.Client('guia',()=>{});assert.equal((await b.load()).note,'mañana');
 offline=true;a.queue({note:'sin conexión'});assert.equal(await a.flush(),false);assert.equal(a.dirty,true);assert.equal(states.at(-1),'error');assert.equal(disk.note,'mañana');
 offline=false;await a.flush();assert.equal(disk.note,'sin conexión');
 b.queue({note:'stale'});assert.equal(await b.flush(),false);assert.equal(disk.note,'sin conexión');
 console.log('PASS: 15 pasos en cada sistema; recuperación y validación; cinco marcadores originales; guardado confirmado, desconexión, reintento y conflicto entre ventanas.');
}
storageContract().catch(e=>{console.error(e);process.exitCode=1;});
