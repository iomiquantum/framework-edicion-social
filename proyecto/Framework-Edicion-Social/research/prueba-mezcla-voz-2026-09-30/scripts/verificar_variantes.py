from pathlib import Path
import json,hashlib,subprocess,time
import numpy as np,soundfile as sf
from scipy import signal
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];FF='/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg';SR=48000;M=json.loads((OUT/'variantes-largas/manifest.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rms(x):return float(np.sqrt(np.mean(x.astype(np.float64)**2)))
def db(x):return float(20*np.log10(max(float(x),1e-12)))
records=[]
for m in M:
 id=m['id'];v=m['variant'];folder=OUT/f'variantes-largas/{id}/{v}';voice,rate=sf.read(OUT/m['voice_file'],always_2d=True,dtype='float32');assert sha(OUT/m['voice_file'])==m['voice_sha256'] and rate==SR
 media=[]
 for rel,data in m['files'].items():
  p=OUT/rel;assert sha(p)==data['sha256'];pr=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));s=pr['streams'][0];assert int(s['sample_rate'])==SR and s['channels']==2 and abs(float(pr['format']['duration'])-m['duration_s'])<.04
  subprocess.run([FF,'-v','error','-i',str(p),'-f','null','-'],check=True,capture_output=True);x=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(p),'-f','f32le','-']),dtype='<f4').reshape(-1,2);assert np.isfinite(x).all() and rms(x)>1e-6
  media.append({'file':rel,'sha256':data['sha256'],'duration_s':float(pr['format']['duration']),'rms_dbfs':db(rms(x)),'sample_peak_dbfs':db(abs(x).max()),'finite_decode_nonzero':'PASS'})
 mix,sr=sf.read(folder/'mezcla.wav',always_2d=True,dtype='float32');music,sr=sf.read(folder/'musica.wav',always_2d=True,dtype='float32');effects,sr=sf.read(folder/'efectos.wav',always_2d=True,dtype='float32');voice_recovered=mix-music-effects;err=float(abs(voice_recovered-voice).max());assert err<5e-7
 # Complete AAC exported -> difference against full PCM process, including integrated SFX.
 raw=subprocess.check_output([FF,'-v','error','-i',str(folder/'mezcla.m4a'),'-f','f32le','-']);aac=np.frombuffer(raw,dtype='<f4').reshape(-1,2);L=min(len(mix),len(aac));corr=float(np.corrcoef(mix[:L].reshape(-1),aac[:L].reshape(-1))[0,1]);assert corr>.995
 assert m['diagnostics']['v2_mix']['input_tp']<=-1.5
 events=[]
 for e in m['sfx_events']:
  assert sha(ROOT/e['source'])==e['source_sha256'];a=round(e['start']*SR);b=min(len(mix),a+round(e['duration_s']*SR));event=effects[a:b];assert len(event)>0 and rms(event)>1e-6
  events.append({'start_s':e['start'],'duration_s':e['duration_s'],'identity':e['source_sha256'],'rms_dbfs':db(rms(event)),'sample_peak_dbfs':db(abs(event).max()),'bind_presence_pcm':'PASS'})
 assert len({e['identity'] for e in events})>=2 and rms(effects[:2*SR])>1e-6
 mono=mix.mean(axis=1);mono_loss=db(rms(mono)/rms(mix));assert mono_loss>-1
 # Stress files simulate a restricted mono channel; they are not a physical-phone listening test.
 dest=folder/'qa-mono-banda-limitada.m4a';subprocess.run([FF,'-v','error','-i',str(folder/'mezcla.m4a'),'-af','pan=mono|c0=0.5*c0+0.5*c1,highpass=f=180,lowpass=f=7200','-c:a','aac','-b:a','128k','-y',str(dest)],check=True)
 raw=subprocess.check_output([FF,'-v','error','-i',str(dest),'-f','f32le','-']);stress=np.frombuffer(raw,dtype='<f4');assert np.isfinite(stress).all() and rms(stress)>1e-6 and abs(stress).max()<1
 # Changes into/out of deliberate silence and finite envelopes are preserved and measured.
 dynamic=json.loads((folder/'curvas.json').read_text());assert all(all(np.isfinite(x[k]) for k in ['time_s','voice_band_dbfs','music_band_dbfs','relative_db','soft_protection_db','band_protection_db']) for x in dynamic)
 cuepoints=sorted(set([t['start'] for t in m['music_clips']]+[t['end'] for t in m['music_clips']]+[e['start'] for e in m['sfx_events']]))
 cuts=[]
 for t in cuepoints:
  i=min(len(mix)-1,max(1,round(t*SR)));cuts.append({'time_s':t,'inter_sample_jump_mix':float(abs(mix[i]-mix[i-1]).max()),'inter_sample_jump_accompaniment':float(abs((music+effects)[i]-(music+effects)[i-1]).max())})
 record={'id':id,'variant':v,'files':media,'file_count':len(media),'voice_recovered_max_abs_error':err,'aac_pcm_correlation':corr,'mono_mix_rms_change_db':mono_loss,'bandlimited_mono_stress':{'file':str(dest.relative_to(OUT)),'sha256':sha(dest),'rms_dbfs':db(rms(stress)),'sample_peak_dbfs':db(abs(stress).max()),'not_physical_phone':True},'sfx_events':events,'cue_edges':cuts,'dynamic_clock_finite':True,'status':'PASS','human_listening':'por confirmar'};records.append(record);print('QA',id,v,len(media),'files','mono',round(mono_loss,3),'voiceerr',err,flush=True)
 allresult={'status':'PASS','variants':len(records),'files_verified':sum(r['file_count'] for r in records),'records':records,'voice_shared_exact_same_gain':True,'native_48k_stereo':True,'source_and_music_and_sfx_hashes':True,'human_listening':'por confirmar'};(OUT/'variantes-largas/validacion-entrega.json').write_text(json.dumps(allresult,ensure_ascii=False,indent=2)+'\n')
