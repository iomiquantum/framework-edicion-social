from pathlib import Path
import json,subprocess,hashlib,time,re,unicodedata
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parents[1];QA=OUT/'variantes-largas/asr-qa';QA.mkdir(parents=True,exist_ok=True);FF='/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg';MODEL=Path('/Users/iomijhondavid/.cache/hyperframes/whisper/models/ggml-large-v3.bin');CLI='/opt/homebrew/bin/whisper-cli'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def words(s):return re.findall(r'[a-z0-9]+',unicodedata.normalize('NFD',s.lower()).encode('ascii','ignore').decode())
def compare(ref,hyp):
 a=words(ref);b=words(hyp);D=[[0]*(len(b)+1) for _ in range(len(a)+1)]
 for i in range(len(a)+1):D[i][0]=i
 for j in range(len(b)+1):D[0][j]=j
 for i in range(1,len(a)+1):
  for j in range(1,len(b)+1):D[i][j]=min(D[i-1][j]+1,D[i][j-1]+1,D[i-1][j-1]+(a[i-1]!=b[j-1]))
 edits=[];i=len(a);j=len(b)
 while i or j:
  if i and j and D[i][j]==D[i-1][j-1]+(a[i-1]!=b[j-1]):
   if a[i-1]!=b[j-1]:edits.append({'type':'substitution','reference':a[i-1],'recognized':b[j-1],'reference_word_index':i-1})
   i-=1;j-=1
  elif i and D[i][j]==D[i-1][j]+1:edits.append({'type':'deletion','reference':a[i-1],'reference_word_index':i-1});i-=1
  else:edits.append({'type':'insertion','recognized':b[j-1],'reference_word_index':i});j-=1
 return {'reference_words':len(a),'recognized_words':len(b),'edit_count':D[-1][-1],'wer':D[-1][-1]/max(1,len(a)),'edits':edits[::-1]}
refs={}
meta=json.loads((ROOT/'NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/videos/retrabajo-acelerado/assets/audio/voice-generic-kokoro.wav.meta.json').read_text());refs['largo-53']=' '.join(r['text'] for r in meta['lines'])
long=ROOT/'Serie-IA-Negocios-10-Videos/VIDEO-LARGO-01-15-2026-09-26/VERSION-05-SUBTITULOS-Y-RECURSOS-FOTOGRAFICOS-2026-09-27/montaje-visual-hyperframes/assets/voice-guide/VOZ_GUIA_COMPLETA.words.json';refs['largo-159']=' '.join(w['text'] for w in json.loads(long.read_text()))
records=[];controls={};modelhash=sha(MODEL)
# Baselines first, then actual final AAC mixtures, same model/settings; no prompt containing the script.
items=[(id,'control',OUT/f'renders/v2/{id}-voz-sola.m4a') for id in ['largo-53','largo-159']]+[(id,v,OUT/f'variantes-largas/{id}/{v}/mezcla.m4a') for id in ['largo-53','largo-159'] for v in ['A','B','C']]
for id,v,src in items:
 assert src.exists();prefix=QA/f'{id}-{v}';converted=prefix.with_suffix('.wav');recipe={'source':str(src.relative_to(OUT)),'source_sha256':sha(src),'model':'Whisper.cpp large-v3 local, es,4threads, defaults, no prompt','model_sha256':modelhash,'conversion':'AAC final→mono16kPCM16 SOLO para comprobación, no fuente de mezcla'};recfile=prefix.with_suffix('.receipt.json')
 if not (prefix.with_suffix('.txt').exists() and recfile.exists() and json.loads(recfile.read_text()).get('source_sha256')==recipe['source_sha256']):
  t=time.monotonic();subprocess.run([FF,'-v','error','-i',str(src),'-ar','16000','-ac','1','-c:a','pcm_s16le','-y',str(converted)],check=True)
  args=[CLI,'-m',str(MODEL),'-l','es','-t','4','-ojf','-otxt','-of',str(prefix),str(converted)]
  with prefix.with_suffix('.log').open('w') as log:subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,check=True)
  recipe['elapsed_seconds']=round(time.monotonic()-t,3);recipe['asr_input_sha256']=sha(converted);recfile.write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+'\n')
 text=prefix.with_suffix('.txt').read_text();rec={'id':id,'variant':v,**recipe,'against_script':compare(refs[id],text),'text':text,'human_intelligibility':'por confirmar'}
 if v=='control':controls[id]=text
 else:rec['against_control_recognition']=compare(controls[id],text)
 records.append(rec);(QA/'results.json').write_text(json.dumps({'status':'completed_through_current_record','records':records,'purpose':'Proxy de reconocimiento, no escucha/inteligibilidad garantizadas.'},ensure_ascii=False,indent=2)+'\n');print('ASR',id,v,'WER',round(rec['against_script']['wer']*100,2),'delta-control',round(rec.get('against_control_recognition',{}).get('wer',0)*100,2),flush=True)
(QA/'results.json').write_text(json.dumps({'status':'COMPLETE','records':records,'method':'Control y mezclas exactasAAC, mismo motor/modelo sin prompt; WER normalizado sin puntuación/acentos.','limits':'ASR puede alucinar/corregir por modelo de lenguaje. No certifica claridad humana, ausencia de masking, emoción ni calidad. No corrige el guion ni reingesta el lote.','human_review':'por confirmar'},ensure_ascii=False,indent=2)+'\n')
