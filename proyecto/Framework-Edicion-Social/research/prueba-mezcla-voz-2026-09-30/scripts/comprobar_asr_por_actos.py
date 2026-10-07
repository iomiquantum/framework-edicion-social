from pathlib import Path
import json,subprocess,hashlib,unicodedata,re,time
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];FF='/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg';CLI='/opt/homebrew/bin/whisper-cli';MODEL='/Users/iomijhondavid/.cache/hyperframes/whisper/models/ggml-large-v3.bin';QA=OUT/'variantes-largas/asr-por-actos';QA.mkdir(parents=True,exist_ok=True)
base=ROOT/'Serie-IA-Negocios-10-Videos/VIDEO-LARGO-01-15-2026-09-26/VERSION-05-SUBTITULOS-Y-RECURSOS-FOTOGRAFICOS-2026-09-27/montaje-visual-hyperframes';timing=json.loads((base/'ACT_TIMING_GUIDE.json').read_text());print('TIMINGTYPE',type(timing).__name__,flush=True)
# Frozen act boundaries pre-exist the recognition failures. No script prompt/no selective favorable snippets.
bounds=[0,24.33,37.236,59.005,83.449,93.365,120.909,146.047,158.798];words=json.loads((base/'assets/voice-guide/VOZ_GUIA_COMPLETA.words.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def toks(s):return re.findall('[a-z0-9]+',unicodedata.normalize('NFD',s.lower()).encode('ascii','ignore').decode())
def distance(a,b):
 a=toks(a);b=toks(b);row=list(range(len(b)+1))
 for i,w in enumerate(a,1):
  new=[i]
  for j,z in enumerate(b,1):new.append(min(new[-1]+1,row[j]+1,row[j-1]+(w!=z)))
  row=new
 return {'reference_words':len(a),'recognized_words':len(b),'edits':row[-1],'wer':row[-1]/max(1,len(a))}
controls={};records=[]
for variant in ['control','A','B','C']:
 source=OUT/'renders/v2/largo-159-voz-sola.m4a' if variant=='control' else OUT/f'variantes-largas/largo-159/{variant}/mezcla.m4a'
 for k,(a,b) in enumerate(zip(bounds[:-1],bounds[1:]),1):
  ref=' '.join(w['text'] for w in words if a<=w['start']<b);prefix=QA/f'{variant}-acto-{k:02d}';inputpath=prefix.with_suffix('.wav');receipt=prefix.with_suffix('.receipt.json');srcsha=sha(source)
  if not (prefix.with_suffix('.txt').exists() and receipt.exists() and json.loads(receipt.read_text()).get('source_sha256')==srcsha):
   subprocess.run([FF,'-v','error','-ss',str(a),'-i',str(source),'-t',str(b-a),'-ar','16000','-ac','1','-c:a','pcm_s16le','-y',str(inputpath)],check=True)
   args=[CLI,'-m',MODEL,'-l','es','-t','4','-ojf','-otxt','-of',str(prefix),str(inputpath)]
   started=time.monotonic()
   with prefix.with_suffix('.log').open('w') as l:subprocess.run(args,stdout=l,stderr=subprocess.STDOUT,check=True)
   receipt.write_text(json.dumps({'source_sha256':srcsha,'start_s':a,'end_s':b,'input_sha256':sha(inputpath),'elapsed_seconds':time.monotonic()-started,'settings':'large-v3/es/4threads/defaults/no prompt; independent pre-existing acts'},indent=2)+'\n')
  recognized=prefix.with_suffix('.txt').read_text();r={'variant':variant,'act':k,'start_s':a,'end_s':b,'source_sha256':srcsha,'text':recognized,'reference_text':ref,'against_script':distance(ref,recognized)}
  if variant=='control':controls[k]=recognized
  else:r['against_control_recognition']=distance(controls[k],recognized)
  records.append(r);(QA/'results.json').write_text(json.dumps({'status':'partial','records':records},ensure_ascii=False,indent=2)+'\n');print('ACT ASR',variant,k,'script',round(r['against_script']['wer']*100,2),'control',round(r.get('against_control_recognition',{}).get('wer',0)*100,2),flush=True)
summary={}
for v in ['control','A','B','C']:
 subset=[r for r in records if r['variant']==v];r0={'script_word_errors':sum(r['against_script']['edits'] for r in subset),'script_words':sum(r['against_script']['reference_words'] for r in subset)};r0['script_wer']=r0['script_word_errors']/r0['script_words']
 if v!='control':r0['control_word_errors']=sum(r['against_control_recognition']['edits'] for r in subset);r0['control_words']=sum(r['against_control_recognition']['reference_words'] for r in subset);r0['control_wer']=r0['control_word_errors']/r0['control_words']
 summary[v]=r0
(QA/'results.json').write_text(json.dumps({'status':'COMPLETE','records':records,'summary':summary,'limits':'Reconocimiento por actos delimita contexto; no sustituye prueba auditiva. Se conserva también ASR completo fallido. Mismas fronteras originales/control/mezclas, ninguna versión textual de guion se entrega al reconocedor.'},ensure_ascii=False,indent=2)+'\n');print('SUMMARY',summary,flush=True)
