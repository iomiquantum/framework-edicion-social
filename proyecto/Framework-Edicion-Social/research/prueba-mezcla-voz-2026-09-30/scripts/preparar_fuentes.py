from pathlib import Path
import json,hashlib,subprocess,datetime,urllib.parse
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parents[1]
BANK=ROOT/'Framework-Edicion-Social/library/music/candidates/2026-09-30-mezclas-contexto'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def curl(url,p):
 subprocess.run(['curl','-fL','--retry','2','--max-time','90','-sS',url,'-o',str(p)],check=True)
docs=['AGENTS.md','Serie-IA-Negocios-10-Videos/AGENTS.md','BITACORA_CURSO_EDICION.md','Framework-Edicion-Social/AUDIO_DIRECCION_Y_PROSODIA.md','Framework-Edicion-Social/CHANGELOG.md']
save(OUT/'RECIBO_INICIO.json',{'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Cinco pruebas de musicalización: tres voces20–30s y dos voces largas existentes. No cambia editables ni renders de origen.','instructions':[{'path':p,'sha256':sha(ROOT/p)} for p in docs],'user_feedback':'Pistas recientes con sonidos fuertes: sin veredicto definitivo. Una o dos músicas en cortos según contexto, biblioteca reutilizable por función. Inicio/dirección C favorable, mezcla final pendiente.','method':'Análisis de texto, prosodia, medidas de señal y reproducción nativa; sin escucha perceptual del agente.','human_review':'por confirmar','catalog_search':'HeyGen UNAUTHORIZED; continúa con descarga pública oficial Incompetech, sin enviar voces.'})
curl('https://incompetech.com/music/royalty-free/pieces.json',BANK/'licencias/pieces.json')
allp=json.loads((BANK/'licencias/pieces.json').read_text())
chosen=[]
for title,slug,roles in [('Backbay Lounge','backbay-lounge',['impulso','solucion']),('Clean Soul','clean-soul',['conversacion','reflexion']),('Cipher','cipher',['mecanismo','contraste'])]:
 p=next(x for x in allp if x['title']==title)
 page='https://incompetech.com/music/royalty-free/index.html?isrc='+p['isrc']
 curl(page,BANK/f'licencias/{slug}-fuente.html')
 h=(BANK/f'licencias/{slug}-fuente.html').read_text()
 assert 'Attribution 4.0' in h and 'p.filename' in h,'No prueba de licencia/vínculo actual'
 url='https://incompetech.com/music/royalty-free/mp3-royaltyfree/'+urllib.parse.quote(p['filename'])
 target=BANK/f'{slug}.mp3';curl(url,target)
 subprocess.run(['/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True,capture_output=True)
 record={'id':'BGM-CAND-KM-'+slug.upper(),'title':title,'author':'Kevin MacLeod','file':str(target.relative_to(ROOT/'Framework-Edicion-Social')),'sha256':sha(target),'bytes':target.stat().st_size,'source_page':page,'download_url':url,'source_record':p,'source_html_sha256':sha(BANK/f'licencias/{slug}-fuente.html'),'license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/','credit':title+' — Kevin MacLeod (incompetech.com). CC BY 4.0. '+page+' · https://creativecommons.org/licenses/by/4.0/. Cambios en estas pruebas: extractos, filtros de música, ganancia y automatización.','roles':roles,'status':'candidate_in_context_pending_listening','human_review':'por confirmar','decode_full':'pass'}
 chosen.append(record);print('DOWNLOADED',slug,target.stat().st_size,flush=True)
for slug,url in [('licencias-incompetech','https://incompetech.com/music/royalty-free/licenses/'),('cc-by-4','https://creativecommons.org/licenses/by/4.0/')]:curl(url,BANK/f'licencias/{slug}.html')
save(BANK/'manifest.json',{'date_local':'2026-09-30','tracks':chosen,'human_review':'por confirmar'})
longbase='Serie-IA-Negocios-10-Videos/VIDEO-LARGO-01-15-2026-09-26/VERSION-05-SUBTITULOS-Y-RECURSOS-FOTOGRAFICOS-2026-09-27/montaje-visual-hyperframes/'
sources=[('01','La IA y el retrabajo','Serie-IA-Negocios-10-Videos/VIDEO-01/editable-hyperframes-video-01/assets/video01-silence-cut-speed104-v4.mp4','humana',21.375),('11','Contenido propio','Serie-IA-Negocios-10-Videos/VIDEO-11/editable-hyperframes-video-11/assets/video11-voice-normalized.m4a','humana',29.1),('14','Escuchar al cliente','Serie-IA-Negocios-10-Videos/VIDEO-14/editable-hyperframes-video-14/assets/video14-master-hdr-v1.mp4','humana',23.26),('largo-53','Retrabajo acelerado','NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/videos/retrabajo-acelerado/assets/audio/voice-generic-kokoro-master.wav','Kokoro ef_dora',52.93),('largo-159','De atención a ventas',longbase+'assets/voice-guide/VOZ_GUIA_COMPLETA_NORMALIZADA.wav','HeyGen Lenny guía, no clon del usuario',158.798)]
records=[]
for id,title,rel,kind,duration in sources:
 source=ROOT/rel
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_streams','-show_format','-of','json',str(source)]))
 target=OUT/f'fuentes/{id}-voz-nativa-48k.wav'
 # Mono/estéreo declarados: duplicación unity; mantiene voz intacta salvo remuestreo nativo.
 ch=probe['streams'][0]['channels'];af='pan=stereo|c0=c0|c1=c0' if ch==1 else 'anull'
 subprocess.run(['/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg','-v','error','-i',str(source),'-map','0:a:0','-t',str(duration),'-af',af,'-ar','48000','-c:a','pcm_f32le','-y',str(target)],check=True)
 records.append({'id':id,'title':title,'source':rel,'source_sha256':sha(source),'voice_kind':kind,'duration_s':duration,'probe':probe,'native_48k_file':str(target.relative_to(OUT)),'native_48k_sha256':sha(target),'voice_change':'Solo remuestreo a48k, mono duplicado unity, duración del montaje vigente. Sin restauración ni nuevas EQ/compresión.'})
 print('SOURCE',id,duration,probe['streams'][0]['sample_rate'],flush=True)
save(OUT/'fuentes/inventario.json',records)
