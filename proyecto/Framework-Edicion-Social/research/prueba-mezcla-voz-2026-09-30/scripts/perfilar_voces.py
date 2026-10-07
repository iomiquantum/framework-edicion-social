from pathlib import Path
import json,re,hashlib
import numpy as np
import parselmouth
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2]
items=json.loads((OUT/'fuentes/inventario.json').read_text())
phrases01=[(0,2.113,'La IA no te está ahorrando tiempo.'),(2.113,6.142,'Hay gente utilizando inteligencia artificial y trabajando más que antes.'),(6.142,11.695,'Generan algo, corrigen, vuelven a pedirlo, revisan otra vez.'),(11.695,13.194,'Eso no es automatizar.'),(13.194,17.561,'Si la IA te da más trabajo del que te quita, todavía no tienes un sistema.'),(17.561,21.375,'¿La IA te está ahorrando tiempo o te está dando más trabajo?')]
longbase=ROOT/'Serie-IA-Negocios-10-Videos/VIDEO-LARGO-01-15-2026-09-26/VERSION-05-SUBTITULOS-Y-RECURSOS-FOTOGRAFICOS-2026-09-27/montaje-visual-hyperframes'
for it in items:
 id=it['id'];p=OUT/it['native_48k_file'];sound=parselmouth.Sound(str(p));mono=sound.values.mean(axis=0);sr=sound.sampling_frequency
 snd=parselmouth.Sound(mono,sr);pitch=snd.to_pitch_ac(time_step=.02,pitch_floor=75,pitch_ceiling=400);f0=pitch.selected_array['frequency'];pt=pitch.xs()
 block=round(sr*.05);x=mono[:len(mono)//block*block].reshape(-1,block);rms=np.sqrt(np.mean(x*x,axis=1));rdb=20*np.log10(np.maximum(rms,1e-12));rt=(np.arange(len(rms))+.5)*.05
 active=rdb>np.percentile(rdb,95)-22
 if id=='01':phrases=phrases01;binding=ROOT/'Serie-IA-Negocios-10-Videos/VIDEO-01/editable-hyperframes-video-01/compositions/captions-es.html'
 elif id in ['11','14','largo-159']:
  binding=ROOT/('Serie-IA-Negocios-10-Videos/VIDEO-11/editable-hyperframes-video-11/transcript.json' if id=='11' else 'Serie-IA-Negocios-10-Videos/VIDEO-14/editable-hyperframes-video-14/assets/transcript.json') if id!='largo-159' else longbase/'assets/voice-guide/VOZ_GUIA_COMPLETA.words.json'
  words=json.loads(binding.read_text());phrases=[];buf=[];a=0
  for w in words:
   if not buf:a=w['start']
   buf.append(w['text'])
   if w['text'].endswith(('.', '?', ':')):
    phrases.append((a,min(it['duration_s'],w['end']),' '.join(buf)));buf=[]
  if buf:phrases.append((a,it['duration_s'],' '.join(buf)))
 else:
  binding=ROOT/'NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/videos/retrabajo-acelerado/assets/audio/voice-generic-kokoro.wav.meta.json'
  phrases=[(q['start'],q['end'],q['text']) for q in json.loads(binding.read_text())['lines']]
 def metrics(a,b,text):
  rr=rdb[(rt>=a)&(rt<b)];ff=f0[(pt>=a)&(pt<b)];ff=ff[ff>0];ss=rr[rr>np.percentile(rdb,95)-22]
  return {'start_s':round(a,3),'end_s':round(b,3),'text':text,'words_per_s':round(len(text.split())/max(.01,b-a),2),'active_rms_median_dbfs':round(float(np.median(ss)),2) if len(ss) else None,'active_rms_range_p90_p10_db':round(float(np.percentile(ss,90)-np.percentile(ss,10)),2) if len(ss) else None,'f0_median_hz':round(float(np.median(ff)),1) if len(ff) else None,'f0_p90_p10_semitones':round(float(12*np.log2(np.percentile(ff,90)/np.percentile(ff,10))),2) if len(ff) else None,'low_energy_fraction':round(float(np.mean(rr<np.percentile(rdb,95)-22)),3)}
 pauses=[];a=None
 for t,act in zip(rt,active):
  if not act and a is None:a=max(0,t-.025)
  if act and a is not None:
   if t-.025-a>=.14:pauses.append([round(a,3),round(t-.025,3)])
   a=None
 if a is not None and it['duration_s']-a>=.14:pauses.append([round(a,3),it['duration_s']])
 d={'id':id,'voice_file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'transcript_binding':str(binding.relative_to(ROOT)),'transcript_sha256':hashlib.sha256(binding.read_bytes()).hexdigest(),'method':{'rms_window_s':.05,'low_energy_threshold_dbfs':round(float(np.percentile(rdb,95)-22),2),'pitch':'Praat autocorrelation75–400Hz,20ms; octave errors possible','interpretation':'Texto/contexto editorial; métricas no prueban emoción, defecto ni percepción.'},'global':metrics(0,it['duration_s'],''),'low_energy_intervals_s':pauses,'phrases':[metrics(*q) for q in phrases],'human_listening':'por confirmar'}
 (OUT/f'evidencia/prosodia-{id}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(id,'phrases',len(phrases),'pauses',len(pauses),d['global'],flush=True)
