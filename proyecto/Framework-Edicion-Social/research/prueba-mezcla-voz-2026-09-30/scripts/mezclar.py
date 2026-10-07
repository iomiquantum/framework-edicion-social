from pathlib import Path
import json,subprocess,re,hashlib,time,csv
import numpy as np
import soundfile as sf
from scipy import signal,ndimage
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];FW=ROOT/'Framework-Edicion-Social';SR=48000;FF='/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
NATIVE=json.loads((OUT/'fuentes/inventario.json').read_text());PLAN=json.loads((OUT/'plan-mezcla.json').read_text());BANK=FW/'library/music/candidates/2026-09-30-mezclas-contexto';MFILES={'neon':FW/'library/music/candidates/2026-09-30-prueba-ritmica/neon-no-melody.mp3','cipher':BANK/'cipher.mp3','backbay':BANK/'backbay-lounge.mp3','clean':BANK/'clean-soul.mp3'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def run(a,**kw):return subprocess.run(a,check=True,capture_output=True,**kw)
def db(x):return float(20*np.log10(max(float(x),1e-12)))
def rms(x):return float(np.sqrt(np.mean(x.astype(np.float64)**2)))
def read(p):
 # Exact source array before excerpt/fades; avoids output-seek applying filters to wrong time.
 probe=json.loads(run(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=channels','-of','json',str(p)],text=True).stdout);ch=probe['streams'][0]['channels'];assert ch in [1,2]
 x=np.frombuffer(run([FF,'-v','error','-i',str(p),'-map','0:a:0','-ar',str(SR),'-f','f32le','-']).stdout,dtype='<f4').reshape(-1,ch).copy()
 if ch==1:x=np.repeat(x,2,axis=1)
 assert np.isfinite(x).all() and rms(x)>1e-6
 return x
BP=signal.butter(3,[350,5000],btype='bandpass',fs=SR,output='sos')
CARVE=signal.butter(2,[400,4000],btype='bandpass',fs=SR,output='sos')
HP=signal.butter(2,70,btype='highpass',fs=SR,output='sos');LP=signal.butter(2,9000,btype='lowpass',fs=SR,output='sos')
def filt(x,sos):return signal.sosfilt(sos,x,axis=0).astype(np.float32)
def frame(x,hop=.05):
 n=round(hop*SR);pad=(-len(x))%n;a=np.pad(x,((0,pad),(0,0)));return np.sqrt(np.mean(a.reshape(-1,n,2).astype(np.float64)**2,axis=(1,2)))
def expand(x,N,hop=.05):return np.interp(np.arange(N)/SR,(np.arange(len(x))+.5)*hop,x).astype(np.float32)
def write(p,x):assert np.isfinite(x).all() and abs(x).max()<1;sf.write(p,x,SR,subtype='PCM_24')
def measure(p):
 s=run([FF,'-hide_banner','-nostats','-i',str(p),'-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'],text=True).stderr
 m=json.loads(re.findall(r'\{\s*"input_i".*?\}',s,re.S)[-1]);return {k:float(m[k]) for k in ['input_i','input_tp','input_lra','input_thresh']}
# Each music frozen unmodified; processing is reversible in derived audio only.
cache={}
for name,p in MFILES.items():
 x=read(p);y=filt(filt(x,HP),LP);band=filt(y,CARVE);y-=band*.60
 cache[name]=y;print('MUSIC READY',name,len(y)/SR,flush=True)
manifest=[]
for src,plan in zip(NATIVE,PLAN):
 began=time.monotonic();id=src['id'];assert id==plan['id'];voice=read(OUT/src['native_48k_file']);N=round(src['duration_s']*SR);native_n=len(voice);assert abs(N-native_n)<=round(.05*SR);voice=np.pad(voice,((0,max(0,N-len(voice))),(0,0)))[:N]
 source_measure=measure(OUT/src['native_48k_file']);fixed_gain=min(-18-source_measure['input_i'],-3.2-source_measure['input_tp']);voice*=10**(fixed_gain/20)
 vr=frame(voice);vdb=20*np.log10(np.maximum(vr,1e-12));active=vdb>np.percentile(vdb,95)-22;ref=float(np.median(vr[active]));vband=filt(voice,BP);vbr=frame(vband);music_v1=np.zeros_like(voice);clips=[]
 for tr in plan['music']:
  a=round(tr['start']*SR);b=min(N,round(tr['end']*SR));o=round(tr['source_start']*SR);bed=cache[tr['music']][o:o+(b-a)].copy();assert len(bed)==b-a
  nominal=ref/max(rms(bed),1e-12);bed*=nominal
  points=np.array(tr['relative_db_points']);tt=np.arange(a,b)/SR;env=10**(np.interp(tt,points[:,0],points[:,1])/20)
  edge=min(1920,len(env)//2);env[:edge]*=np.sin(np.linspace(0,np.pi/2,edge))**2;env[-edge:]*=np.cos(np.linspace(0,np.pi/2,edge))**2
  music_v1[a:b]+=bed*env[:,None]
  clips.append({**tr,'source':str(MFILES[tr['music']].relative_to(ROOT)),'source_sha256':sha(MFILES[tr['music']]),'excerpt_duration_s':len(bed)/SR,'excerpt_rms_before_manual_dbfs':db(rms(bed)),'normalization_gain_db':db(nominal)})
 effects=np.zeros_like(voice);events=[]
 for e in plan['sfx']:
  p=FW/'library/sfx'/e['file'];x=read(p);a=round(e['start']*SR);b=min(N,a+len(x));x=x[:b-a]
  # Event calibrated to current voice if active, otherwise neighboring voiced context; no absolute loudness boost in quiet gaps.
  window=voice[max(0,a-round(.25*SR)):min(N,b+round(.25*SR))];cr=rms(window);reference=min(ref*1.10,max(ref*.55,cr));g=reference/max(rms(x),1e-12)*10**(e['target_relative_rms_db']/20)
  g=min(g,10**(-18.5/20)/max(abs(x).max(),1e-12));x*=g
  effects[a:b]+=x
  events.append({**e,'source':str(p.relative_to(ROOT)),'source_sha256':sha(p),'duration_s':len(x)/SR,'gain_db':db(g),'peak_dbfs':db(abs(x).max()),'rms_dbfs':db(rms(x)),'voice_same_event_rms_dbfs':db(rms(voice[a:b])),'voice_context_rms_dbfs':db(reference),'band_relative_same_event_db':db(rms(filt(x,BP))/max(rms(vband[a:b]),1e-12)),'peak_time_s':e['start']+int(np.argmax(abs(x).max(axis=1)))/SR})
 assert len({e['source_sha256'] for e in events})>=2 and any(e['start']<2 for e in events)
 # V2: protect lower-energy syllables without boosting every gap. Downward-only secondary layer, after editorial envelope.
 mr=frame(music_v1);soft=np.clip(vdb-db(ref)+4,-7,0);soft[~active]=0
 # 200ms anticipation/min-filter plus 350ms release; never raises music above editorial envelope.
 soft=ndimage.minimum_filter1d(soft,size=5,mode='nearest');soft=ndimage.gaussian_filter1d(soft,2.8,mode='nearest');protect=expand(10**(soft/20),N)
 music_v2=music_v1*protect[:,None]
 # Speech-band safety cap: measured400ms neighborhood, only reductions; freezes manual decision through gaps.
 mb=frame(filt(music_v2,BP));capdb=np.minimum(0,20*np.log10(np.maximum(vbr,1e-10)/np.maximum(mb,1e-10))-14);capdb[~active]=0;capdb=np.maximum(-8,capdb);capdb=ndimage.minimum_filter1d(capdb,5);capdb=ndimage.gaussian_filter1d(capdb,2)
 music_v2*=expand(10**(capdb/20),N)[:,None]
 v1dir=OUT/'renders/v1';v2dir=OUT/'renders/v2';v1dir.mkdir(parents=True,exist_ok=True);v2dir.mkdir(parents=True,exist_ok=True)
 write(v1dir/f'{id}-mezcla.wav',voice+music_v1+effects)
 final=voice+music_v2+effects;gain=1.;peak=float(np.max(np.abs(signal.resample_poly(final,4,1,axis=0))))
 if db(peak)>-2:gain=10**((-2-db(peak))/20)
 voice*=gain;music_v2*=gain;effects*=gain;final=voice+music_v2+effects
 for label,x in [('mezcla',final),('voz-sola',voice),('musica',music_v2),('efectos',effects)]:write(v2dir/f'{id}-{label}.wav',x)
 wav=v2dir/f'{id}-mezcla.wav';aac=v2dir/f'{id}-mezcla.m4a';run([FF,'-v','error','-i',str(wav),'-c:a','aac','-b:a','256k','-movflags','+faststart','-metadata','comment=Prueba de musicalización; créditos en CREDITOS.md.','-y',str(aac)])
 lm=measure(aac);aac_correction=0
 # AAC may overshoot; preserve uncorrected export if necessary, attenuate all stems/control with same amount, re-encode once.
 if lm['input_tp']>-1.5:
  aac.rename(v2dir/f'{id}-mezcla-antes-ajuste-aac.m4a');aac_correction=-1.8-lm['input_tp'];g=10**(aac_correction/20);voice*=g;music_v2*=g;effects*=g;final=voice+music_v2+effects
  for label,x in [('mezcla',final),('voz-sola',voice),('musica',music_v2),('efectos',effects)]:write(v2dir/f'{id}-{label}.wav',x)
  run([FF,'-v','error','-i',str(wav),'-c:a','aac','-b:a','256k','-movflags','+faststart','-y',str(aac)]);lm=measure(aac)
 assert lm['input_tp']<=-1.5
 # Native control is same voice at same gain; WAV uses same decoder path in listening bank.
 metrics=[];mb1=frame(filt(music_v1,BP));mb2=frame(filt(music_v2,BP));vb=frame(filt(voice,BP));active2=frame(voice)>ref*gain*10**(-22/20)
 for i in range(len(vb)):
  metrics.append({'time_s':round((i+.5)*.05,3),'active':bool(active2[i]),'voice_band_dbfs':round(db(vb[i]),2),'music_v1_band_dbfs':round(db(mb1[i]),2),'music_v2_band_dbfs':round(db(mb2[i]),2),'music_v2_relative_band_db':round(db(mb2[i]/max(vb[i],1e-12)),2),'secondary_gain_db':round(float(soft[i]+capdb[i]),2)})
 save(OUT/f'evidencia/relacion-{id}.json',metrics)
 decoded=read(aac);L=min(N,len(decoded));corr=float(np.corrcoef(final[:L].reshape(-1),decoded[:L].reshape(-1))[0,1]);assert corr>.995
 stems_sum=sf.read(wav,dtype='float32',always_2d=True)[0];stored=[sf.read(v2dir/f'{id}-{label}.wav',dtype='float32',always_2d=True)[0] for label in ['voz-sola','musica','efectos']];sum_error=float(abs(sum(stored)-stems_sum).max());assert sum_error<5e-7
 voice_expected=read(OUT/src['native_48k_file'])[:N]*10**((fixed_gain+db(gain)+aac_correction)/20);voice_error=float(abs(voice_expected-voice[:len(voice_expected)]).max());assert voice_error<1e-6
 r={'id':id,'title':plan['title'],'duration_s':N/SR,'voice_kind':src['voice_kind'],'native_duration_s':native_n/SR,'terminal_silence_padding_s':max(0,N-native_n)/SR,'source':src['source'],'source_sha256':src['source_sha256'],'voice_fixed_gain_db':fixed_gain,'global_headroom_gain_db':db(gain),'aac_correction_db':aac_correction,'voice_change':'Solo ganancia constante compartida con control. Sin alterar palabras/ritmo/timbre.','direction':plan['direction'],'chapters':plan['chapters'],'music_clips':clips,'sfx_events':events,'processing_music_only':{'highpass_hz':70,'lowpass_hz':9000,'subtract_band_hz':[400,4000],'band_subtraction_fraction':.6,'secondary_downward_only_db_range':[-15,0],'voice_band_margin_target_db':14,'soft_word_gain_used_db_min':round(float((soft+capdb).min()),2)},'mix_loudness_aac':lm,'aac_pcm_correlation':corr,'stems_sum_max_abs_error':sum_error,'voice_constant_gain_max_abs_error':voice_error,'files':{},'nonzero_rms':{name:rms(x) for name,x in [('voice',voice),('music',music_v2),('sfx',effects),('mix',final)]},'sfx_hook':'pass','sfx_identities':len({e['source_sha256'] for e in events}),'native_playback':'pending','human_listening':'por confirmar','elapsed_mix_seconds':round(time.monotonic()-began,2)}
 for p in [wav,aac,v2dir/f'{id}-voz-sola.wav',v2dir/f'{id}-musica.wav',v2dir/f'{id}-efectos.wav',v1dir/f'{id}-mezcla.wav']:r['files'][str(p.relative_to(OUT))]={'sha256':sha(p),'bytes':p.stat().st_size}
 manifest.append(r);save(OUT/'manifest.json',manifest);print('MIX',id,'I',lm['input_i'],'TP',lm['input_tp'],'corr',round(corr,5),'SFX',len(events),'seconds',r['elapsed_mix_seconds'],flush=True)
 del stored,final,voice,music_v1,music_v2,effects,decoded,stems_sum,vband
save(OUT/'evidencia/validacion-tecnica.json',{'status':'PASS','pieces':len(manifest),'source_hashes_unchanged':all(sha(ROOT/s['source'])==s['source_sha256'] for s in NATIVE),'voices_constant_gain':True,'stems_sum':True,'aac_native_48k_stereo':True,'aac_true_peak_max_dbfs':max(m['mix_loudness_aac']['input_tp'] for m in manifest),'all_nonzero':all(min(m['nonzero_rms'].values())>1e-6 for m in manifest),'hook_sfx_all':True,'minimum_two_sfx_identities':True,'aac_correlation_min':min(m['aac_pcm_correlation'] for m in manifest),'human_listening':'por confirmar','perception_not_certified':True})
