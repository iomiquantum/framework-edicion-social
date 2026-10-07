from pathlib import Path
import json,subprocess,re,hashlib,time,csv
import numpy as np,soundfile as sf
from scipy import signal,ndimage
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];FW=ROOT/'Framework-Edicion-Social';SR=48000;FF='/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg';PLAN=json.loads((OUT/'variantes-largas/plan.json').read_text());OLD=json.loads((OUT/'manifest.json').read_text());SFX=json.loads((FW/'library/sfx/candidates/2026-09-30-musicalizacion/manifest.json').read_text())['sfx'];FXFILES={r['id']:ROOT/r['file'] for r in SFX}
files={'neon':FW/'library/music/candidates/2026-09-30-prueba-ritmica/neon-no-melody.mp3','resonance':FW/'library/music/candidates/2026-09-30-funciones/resonance-no-backend-melody.mp3','sarsaparilla':FW/'library/music/candidates/2026-09-30-funciones/sarsaparilla.mp3','cipher':FW/'library/music/candidates/2026-09-30-mezclas-contexto/cipher.mp3','backbay':FW/'library/music/candidates/2026-09-30-mezclas-contexto/backbay-lounge.mp3','clean':FW/'library/music/candidates/2026-09-30-mezclas-contexto/clean-soul.mp3'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def run(a,**kw):return subprocess.run(a,check=True,capture_output=True,**kw)
def db(x):return float(20*np.log10(max(float(x),1e-12)))
def rms(x):return float(np.sqrt(np.mean(x.astype(np.float64)**2)))
def read(p):
 ch=json.loads(run(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=channels','-of','json',str(p)],text=True).stdout)['streams'][0]['channels'];assert ch in [1,2]
 x=np.frombuffer(run([FF,'-v','error','-i',str(p),'-map','0:a:0','-ar',str(SR),'-f','f32le','-']).stdout,dtype='<f4').reshape(-1,ch).copy();x=np.repeat(x,2,axis=1) if ch==1 else x;assert np.isfinite(x).all() and rms(x)>1e-6;return x
BP=signal.butter(3,[350,5000],btype='bandpass',fs=SR,output='sos');CARVE=signal.butter(2,[400,4000],btype='bandpass',fs=SR,output='sos');HP=signal.butter(2,80,btype='highpass',fs=SR,output='sos');LP=signal.butter(2,9500,btype='lowpass',fs=SR,output='sos');LP_SOFT=signal.butter(2,5500,btype='lowpass',fs=SR,output='sos')
def filt(x,sos):return signal.sosfilt(sos,x,axis=0).astype(np.float32)
def frame(x,hop=.05):
 n=round(hop*SR);x=np.pad(x,((0,(-len(x))%n),(0,0)));return np.sqrt(np.mean(x.reshape(-1,n,2).astype(np.float64)**2,axis=(1,2)))
def expand(x,N):return np.interp(np.arange(N)/SR,(np.arange(len(x))+.5)*.05,x).astype(np.float32)
def write(p,x):assert np.isfinite(x).all() and abs(x).max()<1;sf.write(p,x,SR,subtype='PCM_24')
def measure(p):
 s=run([FF,'-hide_banner','-nostats','-i',str(p),'-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'],text=True).stderr;m=json.loads(re.findall(r'\{\s*"input_i".*?\}',s,re.S)[-1]);return {k:float(m[k]) for k in ['input_i','input_tp','input_lra']}
cache={}
for name,p in files.items():cache[name]=filt(filt(read(p),HP),LP);print('CACHE',name,flush=True)
manifest=[]
for plan in PLAN:
 began=time.monotonic();id=plan['id'];variant=plan['variant'];destination=OUT/f'variantes-largas/{id}/{variant}';destination.mkdir(parents=True,exist_ok=True);voice=read(OUT/f'renders/v2/{id}-voz-sola.wav');N=len(voice);vband=filt(voice,BP);vr=frame(voice);vdb=20*np.log10(np.maximum(vr,1e-12));active=vdb>np.percentile(vdb,95)-22;ref=float(np.median(vr[active]));vbr=frame(vband);speech_activity=ndimage.gaussian_filter1d(active.astype(float),1.5);carve_clock=expand(speech_activity,N)
 music=np.zeros_like(voice);clips=[]
 for q in plan['music']:
  a=round(q['start']*SR);b=min(N,round(q['end']*SR));o=round(q['source_start']*SR);bed=cache[q['music']][o:o+b-a].copy();assert len(bed)==b-a
  if q['character']=='contenido':bed=filt(bed,LP_SOFT)
  nominal=ref/max(rms(bed),1e-12);bed*=nominal
  # mid-side controlled, near center to remain stable in mono.
  mid=(bed[:,0]+bed[:,1])*.5;side=(bed[:,0]-bed[:,1])*.5*.86;bed=np.stack([mid+side,mid-side],axis=1)
  factor=.35 if variant in ['A','C'] else .28;band=filt(bed,CARVE);bed-=band*(factor*carve_clock[a:b,None])
  points=np.asarray(q['relative_db_points']);env=10**(np.interp(np.arange(a,b)/SR,points[:,0],points[:,1])/20);edge=min(1920,len(env)//2);env[:edge]*=np.sin(np.linspace(0,np.pi/2,edge))**2;env[-edge:]*=np.cos(np.linspace(0,np.pi/2,edge))**2;music[a:b]+=bed*env[:,None];clips.append({**q,'source':str(files[q['music']].relative_to(ROOT)),'source_sha256':sha(files[q['music']]),'nominal_gain_db':db(nominal),'carve_fraction':factor})
 effects_v1=np.zeros_like(voice);effects=np.zeros_like(voice);events=[]
 for j,e in enumerate(plan['sfx']):
  src=FXFILES[e['file']];x=read(src);a=round(e['start']*SR);b=min(N,a+len(x));x=x[:b-a].copy()
  if e['reverse']:x=x[::-1].copy()
  nearby=voice[max(0,a-round(.35*SR)):min(N,b+round(.25*SR))];reference=min(ref*1.15,max(ref*.60,rms(nearby)));g=reference/max(rms(x),1e-12)*10**(e['target_relative_rms_db']/20);g=min(g,10**(-18.5/20)/max(abs(x).max(),1e-12));x*=g
  pan=(.10 if j%2 else -.10) if variant=='C' else 0;left=1-max(0,pan);right=1+min(0,pan);x[:,0]*=left;x[:,1]*=right
  effects_v1[a:b]+=x
  # Protect any tail crossing into the next words after the transient; never gated harshly.
  start_protect=min(len(x),round(.065*SR));tail_envelope=np.ones(len(x),np.float32);speech=carve_clock[a:b];tail_envelope[start_protect:]=1-.20*speech[start_protect:];tail_envelope=ndimage.gaussian_filter1d(tail_envelope,240);x*=tail_envelope[:,None];effects[a:b]+=x
  events.append({**e,'source':str(src.relative_to(ROOT)),'source_sha256':sha(src),'duration_s':len(x)/SR,'gain_db':db(g),'pan':pan,'rendered_peak_dbfs':db(abs(x).max()),'rendered_rms_dbfs':db(rms(x)),'voice_context_dbfs':db(reference),'tail_gain_min_db':db(tail_envelope.min()),'reason':e['reason']})
 assert len({e['source_sha256'] for e in events})>=2 and any(e['start']<2 for e in events)
 initial=voice+music+effects_v1;write(destination/'mezcla-v1.wav',initial)
 # More present palette, then dialogue protection measured against actual band and weak phrase energy.
 soft=np.clip(vdb-db(ref)+3,-4.5,0);soft[~active]=0;soft=ndimage.gaussian_filter1d(ndimage.minimum_filter1d(soft,5),2.5)
 protected=music*expand(10**(soft/20),N)[:,None]
 vb200=ndimage.uniform_filter1d(vbr*vbr,5)**.5;mb=frame(filt(protected,BP));mb200=ndimage.uniform_filter1d(mb*mb,5)**.5
 # 250ms view avoids chasing individual zero crossings. Margin10.5dB is only a warning/calibration target.
 cap=np.minimum(0,20*np.log10(np.maximum(vb200,1e-10)/np.maximum(mb200,1e-10))-10.5);cap[~active]=0;cap=np.maximum(cap,-10);cap=ndimage.gaussian_filter1d(ndimage.minimum_filter1d(cap,5),1.8);protected*=expand(10**(cap/20),N)[:,None]
 music=protected;mix=voice+music+effects
 # Keep voice level exactly shared across variants: any emergency headroom belongs to accompaniment, not voice.
 peak=float(abs(signal.resample_poly(mix,4,1,axis=0)).max());accomp_db=0
 while db(peak)>-2:
  accomp_db-=.5;music*=10**(-.5/20);effects*=10**(-.5/20);mix=voice+music+effects;peak=float(abs(signal.resample_poly(mix,4,1,axis=0)).max());assert accomp_db>-15
 for label,x in [('mezcla',mix),('musica',music),('efectos',effects)]:write(destination/f'{label}.wav',x)
 wav=destination/'mezcla.wav';aac=destination/'mezcla.m4a';run([FF,'-v','error','-i',str(wav),'-c:a','aac','-b:a','256k','-movflags','+faststart','-metadata','comment=Pruebas de musicalización. Créditos y cambios: CREDITOS.md.','-y',str(aac)]);loud=measure(aac);corrections=[]
 while loud['input_tp']>-1.5:
  old=destination/f'mezcla-aac-antes-ajuste-{len(corrections)}.m4a';aac.rename(old);corrections.append({'true_peak_dbfs':loud['input_tp'],'accompaniment_gain_db':-.5});accomp_db-=.5;music*=10**(-.5/20);effects*=10**(-.5/20);mix=voice+music+effects
  for label,x in [('mezcla',mix),('musica',music),('efectos',effects)]:write(destination/f'{label}.wav',x)
  run([FF,'-v','error','-i',str(wav),'-c:a','aac','-b:a','256k','-movflags','+faststart','-y',str(aac)]);loud=measure(aac);assert len(corrections)<12
 for label in ['musica','efectos']:run([FF,'-v','error','-i',str(destination/f'{label}.wav'),'-c:a','aac','-b:a','256k','-movflags','+faststart','-y',str(destination/f'{label}.m4a')])
 decoded=read(aac);L=min(len(mix),len(decoded));corr=float(np.corrcoef(mix[:L].reshape(-1),decoded[:L].reshape(-1))[0,1]);assert corr>.995
 stored=sf.read(wav,always_2d=True,dtype='float32')[0];m_st=sf.read(destination/'musica.wav',always_2d=True,dtype='float32')[0];e_st=sf.read(destination/'efectos.wav',always_2d=True,dtype='float32')[0];err=float(abs(stored-(voice+m_st+e_st)).max());assert err<5e-7
 mbfinal=frame(filt(music,BP));voice_rms=frame(vband);ratio=20*np.log10(np.maximum(mbfinal,1e-12)/np.maximum(voice_rms,1e-12));strong=active&(voice_rms>10**(-40/20))&(mbfinal>1e-7)
 diagnostics={'voice_band_threshold_dbfs':-40,'median_music_relative_db':float(np.median(ratio[strong])),'p95_music_relative_db':float(np.percentile(ratio[strong],95)),'max_music_relative_db':float(max(ratio[strong])),'v1_mix':measure(destination/'mezcla-v1.wav'),'v2_mix':loud,'applied_secondary_gain_min_db':float((soft+cap).min()),'max_abs_stems_error':err,'emergency_accompaniment_gain_db':accomp_db,'aac_adjustments':corrections}
 curves=[{'time_s':round((i+.5)*.05,3),'speech_gate':bool(active[i]),'voice_band_dbfs':round(db(vbr[i]),2),'music_band_dbfs':round(db(mbfinal[i]),2),'relative_db':round(float(ratio[i]),2),'soft_protection_db':round(float(soft[i]),2),'band_protection_db':round(float(cap[i]),2)} for i in range(len(vbr))];save(destination/'curvas.json',curves)
 entries={str(p.relative_to(OUT)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in destination.glob('*') if p.suffix in ['.wav','.m4a']}
 record={'id':id,'variant':variant,'title':plan['title'],'direction':plan['direction'],'duration_s':N/SR,'music_clips':clips,'sfx_events':events,'voice_file':f'renders/v2/{id}-voz-sola.wav','voice_sha256':sha(OUT/f'renders/v2/{id}-voz-sola.wav'),'source_sha256':next(m['source_sha256'] for m in OLD if m['id']==id),'files':entries,'diagnostics':diagnostics,'aac_pcm_correlation':corr,'sfx_identities':len({e['source_sha256'] for e in events}),'hook_sfx':True,'human_listening':'por confirmar','native_playback':'pending','elapsed_seconds':round(time.monotonic()-began,3)};manifest.append(record);save(OUT/'variantes-largas/manifest.json',manifest);print('RENDER',id,variant,'LUFS',loud['input_i'],'TP',loud['input_tp'],'band95',round(diagnostics['p95_music_relative_db'],1),'SFX',len(events),'s',record['elapsed_seconds'],flush=True)
 del voice,music,mix,protected,effects,effects_v1,decoded,stored,m_st,e_st,initial,vband
save(OUT/'variantes-largas/validacion-mezcla.json',{'status':'PASS','variants':6,'voice_shared_unchanged':True,'aac_tp_max_dbfs':max(m['diagnostics']['v2_mix']['input_tp'] for m in manifest),'minimum_correlation':min(m['aac_pcm_correlation'] for m in manifest),'all_hook_sfx':True,'new_sfx_original_CC0':True,'hearing_perception':'por confirmar'})
