"""Análisis descriptivo de voz declarada; nunca clasifica emociones o personas.

Ejecutar con Python 3.12, numpy 2.3.5 y praat-parselmouth 0.4.7.
No cambia medios/HTML de los editables. F0 estimada con Praat raw AC.
"""
from pathlib import Path
from html.parser import HTMLParser
import hashlib, json, re, subprocess, sys, wave
import numpy as np
import parselmouth

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1]
DEST = OUT / 'evidencia/prosodia'
DEST.mkdir(parents=True, exist_ok=True)
PREV = OUT / 'audiciones/prosodia-v2-48k'
PREV.mkdir(parents=True, exist_ok=True)
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
SR = 16000
DEEP = ['VIDEO-11', 'VIDEO-13', 'VIDEO-14', 'VIDEO-21']

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

class Tags(HTMLParser):
    def __init__(self): super().__init__(); self.rows=[]; self.duration=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='div' and a.get('data-composition-id') in ['main','root']:
            self.duration=float(a.get('data-duration',0))
        if tag=='audio' and a.get('id','').startswith(('voice','voz')): self.rows.append(a)

class Cues(HTMLParser):
    def __init__(self): super().__init__(); self.items={}; self.depth=0; self.current=None
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='div':
            self.depth+=1
            if 'cue' in a.get('class','').split():
                self.current=(a.get('id'),self.depth); self.items[a.get('id')]=[]
        if self.current: self.items[self.current[0]].append(' ')
    def handle_endtag(self, tag):
        if self.current: self.items[self.current[0]].append(' ')
        if tag=='div':
            if self.current and self.current[1]==self.depth: self.current=None
            self.depth-=1
    def handle_data(self, data):
        if self.current: self.items[self.current[0]].append(data)

def decode(path, start=0, duration=None, rate=1, sr=SR):
    cmd=[FF,'-v','error','-ss',str(start),'-i',str(path),'-map','0:a:0']
    if duration is not None: cmd += ['-t',str(duration)]
    if rate!=1: cmd += ['-af',f'atempo={rate}']
    cmd += ['-ac','1','-ar',str(sr),'-f','f32le','pipe:1']
    r=subprocess.run(cmd,capture_output=True,check=True)
    return np.frombuffer(r.stdout,dtype='<f4').astype(np.float64)

def gaps(mask, times, duration, minimum=.15):
    intervals=[]; start=None
    for i, low in enumerate(mask):
        t=max(0,float(times[i])-.025)
        if low and start is None: start=t
        if not low and start is not None:
            if t-start>=minimum: intervals.append([round(start,3),round(t,3)])
            start=None
    if start is not None and duration-start>=minimum: intervals.append([round(start,3),round(duration,3)])
    return intervals

def describe(x):
    sound=parselmouth.Sound(x,SR)
    pitch=sound.to_pitch_ac(time_step=.01,pitch_floor=60,pitch_ceiling=500,
                           silence_threshold=.03,voicing_threshold=.45)
    ts=pitch.xs(); f0=pitch.selected_array['frequency'].copy()
    energy=np.array([20*np.log10(max(1e-12,np.sqrt(np.mean(x[max(0,int((t-.025)*SR)):min(len(x),int((t+.025)*SR))]**2)))) for t in ts])
    gate=float(np.percentile(energy,90)-22)
    f0[energy<gate]=0
    valid=f0>0
    q=np.percentile(f0[valid],[10,50,90]) if np.any(valid) else np.zeros(3)
    e=np.percentile(energy[valid],[10,50,90]) if np.any(valid) else np.zeros(3)
    alternate=sound.to_pitch_ac(time_step=.01,pitch_floor=75,pitch_ceiling=450)
    af=alternate.selected_array['frequency']; at=alternate.xs()
    ix=np.searchsorted(at,ts); ix=np.clip(ix,0,len(at)-1)
    previous=np.clip(ix-1,0,len(at)-1)
    ix=np.where(abs(at[previous]-ts)<abs(at[ix]-ts),previous,ix)
    af=af[ix]; common=valid & (af>0)
    disagreement=float(np.mean(abs(12*np.log2(f0[common]/af[common]))>1)*100) if np.any(common) else None
    both=valid[1:] & valid[:-1]
    jumps=np.zeros(len(ts)-1); jumps[both]=abs(12*np.log2(f0[1:][both]/f0[:-1][both]))
    low=gaps(energy<gate,ts,len(x)/SR)
    metrics={
      'duration_s':round(len(x)/SR,4), 'f0_p10_hz':round(float(q[0]),2),
      'f0_median_hz':round(float(q[1]),2),'f0_p90_hz':round(float(q[2]),2),
      'f0_central_range_semitones':round(float(12*np.log2(q[2]/q[0])),2) if q[0]>0 else None,
      'voiced_energy_central_range_db':round(float(e[2]-e[0]),2),
      'energy_median_voiced_dbfs':round(float(e[1]),2),
      'low_energy_threshold_dbfs':round(gate,2),
      'low_energy_intervals_s':low,
      'low_energy_fraction_pct':round(sum(b-a for a,b in low)/(len(x)/SR)*100,2),
      'pause_threshold_sensitivity_counts':{str(db):len(gaps(energy<np.percentile(energy,90)-db,ts,len(x)/SR)) for db in [18,22,26]},
      'pitch_parameter_disagreement_gt_1_semitone_pct':round(disagreement,2) if disagreement is not None else None,
      'adjacent_pitch_jumps_gt_8_semitones':int(np.sum(jumps>8)),
      'voiced_frames_pct':round(float(np.mean(valid)*100),2),
    }
    internal=[b-a for a,b in low if a>.05 and b<len(x)/SR-.05]
    metrics.update(internal_low_energy_count=len(internal),internal_low_energy_median_s=round(float(np.median(internal)),3) if internal else None,internal_low_energy_cv_pct=round(float(np.std(internal)/np.mean(internal)*100),1) if len(internal)>1 else None)
    series={'time_s':[round(float(t),3) for t in ts],
            'f0_hz':[round(float(v),2) if v else None for v in f0],
            'energy_dbfs':[round(float(v),2) for v in energy]}
    return metrics, series

def cue_rows(path, series):
    text=path.read_text(); parser=Cues(); parser.feed(text)
    marks=re.findall(r'\[\s*"#([^"]+)"\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\]',text)
    if not marks:
        starts=re.findall(r'tl\.set\("#([^"]+)",\{opacity:1\},([\d.]+)\)',text)
        ends=dict(re.findall(r'tl\.set\("#([^"]+)",\{opacity:0\},([\d.]+)\)',text))
        marks=[(i,a,ends[i]) for i,a in starts if i in ends]
    times=np.array(series['time_s']); f=np.array([v or 0 for v in series['f0_hz']]); e=np.array(series['energy_dbfs'])
    result=[]
    for i,a,b in marks:
        words=' '.join(''.join(parser.items.get(i,[])).split()); a=float(a); b=float(b)
        m=(times>=a)&(times<b)&(f>0); selected=f[m]
        if len(selected):
            p10,med,p90=np.percentile(selected,[10,50,90]); er=float(np.median(e[m]))
        else: p10=med=p90=er=0
        result.append({'cue':i,'start':a,'end':b,'text':words,
          'caption_words':len(re.findall(r'\b[\wÁÉÍÓÚÜÑáéíóúüñ]+\b',words)),
          'caption_rate_wpm_proxy':round(len(re.findall(r'\b\w+\b',words))/(b-a)*60,1),
          'f0_median_hz':round(float(med),2),
          'f0_central_range_semitones':round(float(12*np.log2(p90/p10)),2) if p10 else None,
          'energy_median_voiced_dbfs':round(er,2)})
    return result

def save_wave(path,x):
    if np.max(abs(x))>=1: raise RuntimeError('Clipping risk: '+str(path))
    subprocess.run([FF,'-v','error','-y','-f','f32le','-ar','48000','-ac','1','-i','pipe:0','-c:a','pcm_s24le',str(path)],input=x.astype('<f4').tobytes(),capture_output=True,check=True)

def measure(source):
    if isinstance(source,np.ndarray):
        cmd=[FF,'-hide_banner','-f','f32le','-ar','48000','-ac','1','-i','pipe:0','-af','loudnorm=I=-22:TP=-1:LRA=11:print_format=json','-f','null','-']
        r=subprocess.run(cmd,input=source.astype('<f4').tobytes(),capture_output=True,check=True)
        log=r.stderr.decode()
    else:
        r=subprocess.run([FF,'-hide_banner','-i',str(source),'-af','loudnorm=I=-22:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
        log=r.stderr
    return json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',log,re.S)[-1])

rows=json.loads((OUT/'evidencia/revision-existentes.json').read_text())
result={'method':{'pitch':'Praat raw autocorrelation 60–500 Hz / 10 ms; sensitivity 75–450 Hz; not filtered AC',
  'energy':'50 ms RMS windows at 10 ms hop; voiced central p10–p90',
  'pause':'Low-energy candidates >=150 ms, threshold p90 RMS minus22 dB; sensitivity18/26 dB; not VAD or breath detection',
  'caption_timing':'Existing authored display cues, NOT word alignment or syllabic articulation speed',
  'limits':'No emotion/personality classifier, no automatic EQ diagnosis, no perceptual listening by agent; source capture/processing affects level/timbre.',
  'versions':{'python':sys.version.split()[0],'numpy':np.__version__,'parselmouth':parselmouth.VERSION,'praat':parselmouth.PRAAT_VERSION}},'pieces':[]}
signals={}
for row in rows:
    if not row['id'].startswith('VIDEO-'): continue
    project=ROOT/row['project']; html=project/'index.html'; parser=Tags(); parser.feed(html.read_text())
    if not parser.rows: raise RuntimeError('No voice declarations: '+row['id'])
    duration=max(float(a.get('data-start',0))+float(a['data-duration']) for a in parser.rows)
    x=np.zeros(int(round(duration*SR))); inputs=[]
    for a in parser.rows:
        p=(project/a['src']).resolve(); dur=float(a['data-duration']); start=float(a.get('data-start',0))
        media_start=float(a.get('data-media-start',0)); rate=float(a.get('data-playback-rate',1)); volume=float(a.get('data-volume',1))
        y=decode(p,media_start,dur,rate)*volume; ix=round(start*SR); n=min(len(y),len(x)-ix); x[ix:ix+n]+=y[:n]
        inputs.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'start':start,'duration':dur,'media_start':media_start,'rate':rate,'volume':volume})
    metrics,series=describe(x); piece={'id':row['id'],'project':row['project'],'render':row['render'],'html_sha256':sha(html),'inputs':inputs,'metrics':metrics,'series':series}
    if row['id'] in DEEP:
        cp=project/'compositions/captions-es.html'; piece['cue_source']=str(cp.relative_to(ROOT)); piece['cue_source_sha256']=sha(cp); piece['cues']=cue_rows(cp,series)
        wide=np.zeros(int(round(duration*48000)))
        for a in parser.rows:
            y=decode((project/a['src']).resolve(),float(a.get('data-media-start',0)),float(a['data-duration']),float(a.get('data-playback-rate',1)),sr=48000)*float(a.get('data-volume',1))
            ix=round(float(a.get('data-start',0))*48000); n=min(len(y),len(wide)-ix); wide[ix:ix+n]+=y[:n]
        signals[row['id']]=wide
    result['pieces'].append(piece)
    print(row['id'], 'F0 central range',metrics['f0_central_range_semitones'],'st; energy range',metrics['voiced_energy_central_range_db'],'dB',flush=True)

plan=json.loads((ROOT/'Serie-IA-Negocios-10-Videos/VIDEO-13/editable-hyperframes-video-13/cut-plan.json').read_text())
original=ROOT/'Serie-IA-Negocios-10-Videos/00-INGESTA/LOTE-VIDEOS-11-15-ORIGINAL.mp4'
origin=np.concatenate([decode(original,r['start'],r['end']-r['start']) for r in plan['ranges_seconds']])
orig_metrics,orig_series=describe(origin)
result['origin_video13']={'path':str(original.relative_to(ROOT)),'ranges':plan['ranges_seconds'],'metrics':orig_metrics,'series':orig_series}
signals['VIDEO-13-ORIGEN']=np.concatenate([decode(original,r['start'],r['end']-r['start'],sr=48000) for r in plan['ranges_seconds']])
for id,x in signals.items():
    path=PREV/(id.lower()+'-voz.wav'); measured=measure(x)
    gain=-22-float(measured['input_i'])
    if float(measured['input_tp'])+gain>-1: raise RuntimeError('Peak risk at common target: '+id)
    save_wave(path,x*10**(gain/20)); delivered=measure(path)
    result.setdefault('auditions',[]).append({'id':id,'file':str(path.relative_to(OUT)), 'gain_db':round(gain,4),'lufs':float(delivered['input_i']),'true_peak_db':float(delivered['input_tp']),'sha256':sha(path),'treatment':'constant gain only, mono48k PCM24; not denoised/EQ/compressed'})
for p in result['pieces']:
    for a in p['inputs']:
        if sha(ROOT/a['path'])!=a['sha256']: raise RuntimeError('Source changed: '+a['path'])
(DEST/'analisis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
(DEST/'requirements.txt').write_text('numpy==2.3.5\npraat-parselmouth==0.4.7\n')
print('Saved analysis of',len(result['pieces']),'pieces, four phrase maps and five auditions; sources unchanged.')
