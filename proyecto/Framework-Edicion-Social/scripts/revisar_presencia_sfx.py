#!/usr/bin/env python3
"""Technical SFX presence review; never certifies human audibility.

Scope: root composition, one explicit voice stem, static audio gains, no FX,
automation, nested audio or buses. Unsupported graphs fail rather than being
silently measured as if dry. Derivatives share their source identity in the plan.
"""
import argparse, array, hashlib, json, math, subprocess
from html.parser import HTMLParser
from pathlib import Path

class Audio(HTMLParser):
    def __init__(self):
        super().__init__(); self.clips=[]; self.unsupported=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='hf-audio-group': self.unsupported.append('audio bus')
        if tag=='video' and ('muted' not in a or a.get('data-has-audio')=='true'): self.unsupported.append('Audible video not mapped to explicit voice stem')
        if tag=='audio':
            if any(k in a for k in ['data-fx-chain','data-automation','data-playback-rate','data-audio-group','data-fade-in','data-fade-out']): self.unsupported.append(a.get('id','audio')+' FX/automation/group/rate/fade')
            self.clips.append(a)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project',required=True);ap.add_argument('--ffmpeg',required=True)
    ap.add_argument('--out',required=True);ap.add_argument('--plan',default='qa/sfx-calibration.json')
    ap.add_argument('--hook-end',type=float,default=3,help='End of contextual opening hook; adjust per edit')
    args=ap.parse_args();p=Path(args.project).resolve();q=Path(args.out).resolve();q.mkdir(parents=True,exist_ok=True)
    h=Audio();h.feed((p/'index.html').read_text());errors=list(h.unsupported);warnings=[]
    # Nested compositions are allowed only if they add no audio graph.
    class Mounts(HTMLParser):
        def __init__(self): super().__init__(); self.paths=[]
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            if a.get('data-composition-src'): self.paths.append(a['data-composition-src'])
    seen=set()
    def nested(file):
        if file in seen:return
        seen.add(file);text=file.read_text();m=Mounts();m.feed(text)
        for src in m.paths:
            f=(file.parent/src).resolve();a=Audio();a.feed(f.read_text())
            if a.clips or a.unsupported:errors.append('Nested audio graph: '+src)
            nested(f)
    nested(p/'index.html')
    plan=json.loads((p/args.plan).read_text());voice=[a for a in h.clips if a.get('data-track-kind')=='voice'];sfx=[a for a in h.clips if a.get('data-track-kind')=='sfx']
    if len(voice)!=1 or len(h.clips)!=len(voice)+len(sfx):errors.append('Require one root voice and only mapped SFX audio')
    if voice and (float(voice[0].get('data-start',0))!=0 or float(voice[0].get('data-media-start',0))!=0):errors.append('Voice must be a full timeline stem starting at zero')
    if len(sfx)!=len(plan):errors.append('Active SFX and plan event counts differ')
    sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
    def read(file,t=0,d=None,phone=False):
        cmd=[args.ffmpeg,'-v','error','-ss',str(t),'-i',str(file)]
        if d is not None:cmd+=['-t',str(d)]
        if phone:cmd+=['-af','highpass=f=350,lowpass=f=5000']
        cmd+=['-ac','1','-ar','16000','-f','f32le','pipe:1'];raw=subprocess.run(cmd,capture_output=True,check=True).stdout;x=array.array('f');x.frombytes(raw);return x
    def db(x,peak=False):
        if not x:return -240
        value=max(abs(v) for v in x) if peak else math.sqrt(sum(v*v for v in x)/len(x))
        return 20*math.log10(max(value,1e-12))
    results=[]
    if not errors:
        v=voice[0];vf=p/v['src'];voffset=float(v.get('data-media-start',0));vgain=float(v.get('data-volume',1))
        for a in sfx:
            e=next((x for x in plan if 'sfx-'+x['event']==a.get('id')),None)
            if e is None:errors.append('Unmapped '+a.get('id','audio'));continue
            f=p/a['src'];t=float(a.get('data-start',0));dur=float(a['data-duration']);gain=float(a.get('data-volume',1));offset=float(a.get('data-media-start',0))
            if e['file']!=a['src'] or abs(e['start_s']-t)>1e-6 or abs(e['duration_s']-dur)>1e-6 or abs(e['volume']-gain)>1e-6:errors.append('Plan does not bind active '+a['id'])
            if 'sha256' in e and e['sha256']!=sha(f):errors.append('Changed SFX bytes '+a['id'])
            if e.get('source_sha256')!=sha(p/e['source_file']):errors.append('Source identity mismatch '+a['id'])
            probe=subprocess.run([str(Path(args.ffmpeg).with_name('ffprobe.exe' if __import__('os').name == 'nt' else 'ffprobe')),'-v','error','-select_streams','a:0','-show_entries','stream=channels','-of','json',str(f)],capture_output=True,text=True,check=True)
            channels=json.loads(probe.stdout)['streams'][0]['channels'];fold_gain=math.sqrt(2) if channels==1 else 1
            # Compare voice and SFX after the same stereo speaker/downmix policy.
            x=array.array('f',(n*gain*fold_gain for n in read(f,offset,dur)));y=array.array('f',(n*vgain for n in read(vf,t+voffset,dur)))
            xp=array.array('f',(n*gain*fold_gain for n in read(f,offset,dur,True)));yp=array.array('f',(n*vgain for n in read(vf,t+voffset,dur,True)))
            rel=db(x)-db(y);mobile=db(xp)-db(yp);peak=db(x,True)
            peak_at=max(range(len(x)),key=lambda i:abs(x[i]))/16000
            if peak < -25:warnings.append(a['id']+' low absolute peak; inspect perception')
            if rel < -15 and mobile < -15:warnings.append(a['id']+' potential voice masking in both full and limited bands')
            if gain>1:warnings.append(a['id']+' above-unity runtime gain; verify actual playback path or bake gain')
            results.append(dict(id=a['id'],asset_id=e['asset_id'],source_sha256=e['source_sha256'],file=a['src'],sha256=sha(f),start_s=t,duration_s=dur,volume=gain,metric_domain='stereo speaker output folded to mono with ffmpeg; not per-channel source peaks',source_channels=channels,sfx_source_peak_dbfs=peak-20*math.log10(fold_gain),sfx_rms_dbfs=db(x),sfx_peak_dbfs=peak,voice_window_rms_dbfs=db(y),relative_to_voice_db=rel,limited_band_relative_db=mobile,sfx_peak_at_s=t+peak_at))
        identities={x['source_sha256'] for x in results}
        duration=max(float(a.get('data-start',0))+float(a['data-duration']) for a in h.clips)
        if 20<=duration<=30 and len(identities)<2:errors.append('20–30s requires at least two source SFX identities')
        hook=[x for x in results if x['start_s']<args.hook_end and x['start_s']+x['duration_s']>0]
        if not hook:errors.append('Initial hook has no timed SFX')
        elif not any(x['sfx_peak_dbfs']>=-25 for x in hook):warnings.append('Hook SFX exists but its absolute peak needs perceptual review')
    if not errors:
        cmd=[args.ffmpeg,'-y','-v','error','-i',str(p/voice[0]['src'])]
        for a in sfx:cmd+=['-i',str(p/a['src'])]
        filters=[f'[0:a]volume={float(voice[0].get("data-volume",1))}[v]']
        for i,a in enumerate(sfx):
            probe=subprocess.run([str(Path(args.ffmpeg).with_name('ffprobe.exe' if __import__('os').name == 'nt' else 'ffprobe')),'-v','error','-select_streams','a:0','-show_entries','stream=channels','-of','json',str(p/a['src'])],capture_output=True,text=True,check=True)
            channels=json.loads(probe.stdout)['streams'][0]['channels']
            # Web Audio speaker mixing duplicates mono at unity; FFmpeg implicit
            # mono-to-stereo negotiation otherwise attenuates it by sqrt(2).
            stereo='pan=stereo|c0=c0|c1=c0,' if channels==1 else ''
            filters.append(f'[{i+1}:a]atrim=start={float(a.get("data-media-start",0))}:duration={float(a["data-duration"])},asetpts=PTS-STARTPTS,aresample=48000,{stereo}volume={float(a.get("data-volume",1))},adelay={round(round(float(a.get("data-start",0)),3)*48000)}S:all=1[s{i}]')
        filters+=['[v]'+''.join(f'[s{i}]' for i in range(len(sfx)))+f'amix=inputs={len(sfx)+1}:normalize=0:duration=first[out]']
        mix=q/'mix.wav';cmd+=['-filter_complex',';'.join(filters),'-map','[out]','-ar','48000','-c:a','pcm_f32le',str(mix)];subprocess.run(cmd,check=True)
        run=subprocess.run([args.ffmpeg,'-hide_banner','-i',str(mix),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
        (q/'mix-loudness.log').write_text(run.stderr);loud=json.JSONDecoder().raw_decode(run.stderr[run.stderr.rfind('{'):])[0]
        if float(loud['input_tp'])>=0:errors.append('Full diagnostic mix true peak reaches 0dBFS')
    else:loud=None
    report=dict(status='fail' if errors else 'technical_presence_checked_perception_pending',errors=errors,warnings=warnings,events=results,distinct_source_identities=len({x['source_sha256'] for x in results}),hook_window_s=[0,args.hook_end],helper_sha256=sha(Path(__file__)),mono_mix_policy='unity duplication matches Web Audio speaker interpretation; starts rounded to millisecond for engine diagnostic parity',index_sha256=sha(p/'index.html'),plan_sha256=sha(p/args.plan),mix_loudness=loud,human_listened=False,limits='Static root PCM diagnostic, not exact exported AAC. 350–5000Hz band is a sensitivity proxy, not a phone test. Level/masking flags are contextual heuristics, never proof of human audibility, voice intelligibility or naturalness.')
    (q/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False));return bool(errors)

if __name__=='__main__':raise SystemExit(main())
