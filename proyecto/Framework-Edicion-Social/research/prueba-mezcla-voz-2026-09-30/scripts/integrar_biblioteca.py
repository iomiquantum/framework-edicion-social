from pathlib import Path
import json,hashlib,subprocess,re,fcntl
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parents[1];FW=ROOT/'Framework-Edicion-Social';BANK=FW/'library/music/candidates/2026-09-30-mezclas-contexto';FF='/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((BANK/'manifest.json').read_text());names={'Backbay Lounge':('backbay-lounge',38,'Piano, guitarra, bajo y batería según catálogo oficial; propuesta de groove ligero.','Arreglo/melodía pueden competir; evaluar por frase, no validar por nombre.'),'Clean Soul':('clean-soul',31,'Piano eléctrico y bajo, descripción oficial de textura espaciosa; propuesta conversación/evidencia.','Calma no equivale a falta de ritmo ni a encaje: valorar con la voz.'),'Cipher':('cipher',27,'Sintetizadores, piano eléctrico y percusión según fuente; propuesta mecanismo/contraste.','Hook melódico podría robar foco; uso limitado, con espacio en banda de voz.')}
new=[]
for r in manifest['tracks']:
 slug,offset,char,caution=names[r['title']];p=FW/r['file'];target=BANK/f'{slug}-preview-20s.wav'
 if not target.exists():
  log=subprocess.run([FF,'-hide_banner','-ss',str(offset),'-i',str(p),'-t','20','-af','loudnorm=I=-23:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
  stats=json.loads(re.findall(r'\{\s*"input_i".*?\}',log,re.S)[-1]);g=min(-23-float(stats['input_i']),-2-float(stats['input_tp']))
  subprocess.run([FF,'-v','error','-ss',str(offset),'-i',str(p),'-t','20','-af',f'volume={g}dB,afade=t=in:d=0.1,afade=t=out:st=19.5:d=0.5','-ar','48000','-ac','2','-c:a','pcm_s24le','-y',str(target)],check=True)
 else:g=r['preview_changes']['constant_gain_db']
 x,sr=sf.read(target,dtype='float32',always_2d=True);assert x.shape==(960000,2) and sr==48000 and sf.info(target).subtype=='PCM_24' and np.isfinite(x).all() and np.sqrt(np.mean(x*x))>1e-6 and 1e-5<abs(x).max()<1
 r['preview']=str(target.relative_to(FW));r['preview_sha256']=sha(target);r['preview_changes']={'source_start_s':offset,'duration_s':20,'constant_gain_db':g,'fade_in_s':.1,'fade_out_s':.5,'compression':False};r['source_html']=str((BANK/f'licencias/{slug}-fuente.html').relative_to(FW));r['decode_full']='PASS'
 new.append({'id':r['id'],'type':'bgm','title':r['title'],'file':r['file'],'preview':r['preview'],'sha256':r['sha256'],'preview_sha256':r['preview_sha256'],'preview_changes':r['preview_changes'],'roles':r['roles'],'character':char,'status':'candidate_in_context_pending_listening','feedback':'Nueva prueba en cinco mensajes; escucha y elección final por confirmar.','caution':caution,'license':r['license'],'license_url':r['license_url'],'credit':r['credit'],'source_page':r['source_page'],'source_manifest':str((BANK/'manifest.json').relative_to(FW)),'history':False,'context_bank':'research/prueba-mezcla-voz-2026-09-30/index.html'})
(BANK/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
catpath=FW/'library/music/catalogo-editorial.json';lock=FW/'library/music/.catalogo-editorial.json.lock'
with lock.open('a+') as l:
 fcntl.flock(l,fcntl.LOCK_EX);old=catpath.read_text();before=OUT/'evidencia/catalogo-editorial-antes-cinco-mezclas.json'
 if not before.exists():before.write_text(old)
 cat=json.loads(old)
 for r in new:
  if not any(q['id']==r['id'] for q in cat['tracks']):cat['tracks'].insert(3,r)
 feedback={'date_local':'2026-09-30','scope':'Tanda musical reciente, sin identificar rechazo de cada pista completa.','user_feedback':'Las canciones de pronto no me convencieron porque están con sonidos fuertes, pero no demos veredicto final; probar en tres cortos y dos largos.','result':'Cinco pruebas aisladas, pendientes de valoración auditiva; no aprobación global.'}
 cat.setdefault('feedback_history',[])
 if feedback not in cat['feedback_history']:cat['feedback_history'].append(feedback)
 cat['date_local']='2026-09-30';catpath.write_text(json.dumps(cat,ensure_ascii=False,indent=2)+'\n')
 md=FW/'library/music/CATALOGO_EDITORIAL.md';s=md.read_text()
 marker='## Cinco mezclas con voces reales — 2026-09-30'
 if marker not in s:
  s+='\n\n'+marker+'\n\nEl usuario pide conservar el veredicto abierto: percibe sonidos fuertes en la tanda reciente y prefiere evaluar las canciones dentro de mensajes completos. No se convierte ese comentario en rechazo de cada canción ni en aprobación de nuevas.\n\n[Escuchar cinco pruebas](../../research/prueba-mezcla-voz-2026-09-30/index.html): tres voces humanas21/23/29s y dos artificiales existentes53s/2:39. Una música en cada corto; dos en53s, cuatro recursos con tres funciones en2:39.\n\n| Nuevos candidatos | Función propuesta | Estado |\n| --- | --- | --- |\n| Backbay Lounge | Avance práctico, conversación con movimiento | Probada técnicamente en mezcla; escucha por confirmar. |\n| Clean Soul | Evidencia, conversación, pregunta final | Evitar uso continuo por defecto; encaje por confirmar. |\n| Cipher | Cantidad, mecanismo, contraste | Melodía requiere espacio para palabras; valoración pendiente. |\n\nFuente y créditos: [manifest con páginas oficiales y snapshots](candidates/2026-09-30-mezclas-contexto/manifest.json), CC BY4.0 según página oficial actual. Los previews20s son fuentes con ganancia/fades; la mezcla contextual también modifica la música con filtros y automatización. No se han reutilizado músicas de las referencias ni generado voces nuevas.\n'
  md.write_text(s)
# Older one-shot indexer must not erase expanded entries or feedback if someone regenerates it.
p=FW/'research/musica-bajo-voz-2026-09-30/scripts/indexar_biblioteca.py';s=p.read_text();backup=OUT/'evidencia/indexar-biblioteca-antes-ampliacion.py'
if not backup.exists():backup.write_text(s)
needle="(FW/'library/music/catalogo-editorial.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\\n')"
if '# Preserve expanded catalog' not in s:
 replacement="""# Preserve expanded catalog and user feedback when regenerating the original index.
existing_path = FW/'library/music/catalogo-editorial.json'
if existing_path.exists():
    existing = json.loads(existing_path.read_text())
    old_by_id = {t['id']:t for t in existing.get('tracks',[])}
    for t in catalog['tracks']:
        previous = old_by_id.get(t['id'],{})
        for key in ['status','feedback','feedback_history','context_bank']:
            if key in previous: t[key] = previous[key]
    ids = {t['id'] for t in catalog['tracks']}
    catalog['tracks'].extend(t for t in existing.get('tracks',[]) if t['id'] not in ids)
    if 'feedback_history' in existing: catalog['feedback_history'] = existing['feedback_history']
existing_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\\n')"""
 assert needle in s;p.write_text(s.replace(needle,replacement))
print('CATALOG candidates',sum(t['type']=='bgm' and not t['history'] for t in cat['tracks']),'SFX',sum(t['type']=='sfx' for t in cat['tracks']))
