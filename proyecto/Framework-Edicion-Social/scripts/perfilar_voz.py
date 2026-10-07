#!/usr/bin/env python3
"""Relative acoustic profile of a known voice stem, not emotion recognition.

Requires numpy from the existing bundled Python runtime. Reuses timed transcript.
Pitch is an autocorrelation estimate with confidence/voicing limits; do not use
it as proof of emphasis, intention, emotion or exact musical pitch.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
import numpy as np

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ['voice','transcript','direction','ffmpeg','out']:ap.add_argument('--'+k,required=True)
    a=ap.parse_args();f=Path(a.voice);raw=subprocess.run([a.ffmpeg,'-v','error','-i',str(f),'-ac','1','-ar','16000','-f','f32le','pipe:1'],capture_output=True,check=True).stdout
    x=np.frombuffer(raw,dtype=np.float32);sr=16000;frames=[]
    def rms(v):return float(20*np.log10(np.sqrt(np.mean(v*v))+1e-12))
    for start in range(0,len(x)-960,800):
        y=x[start:start+960].astype(float);level=rms(y);pitch=None;conf=None
        if level>-32:
            y=(y-y.mean())*np.hanning(len(y));z=np.fft.rfft(y,2048);ac=np.fft.irfft(z*z.conj(),2048)[:len(y)];e=np.r_[0,np.cumsum(y*y)];lags=np.arange(36,201)
            corr=ac[lags]/np.sqrt(np.maximum((e[-lags-1])*(e[-1]-e[lags]),1e-20))
            peaks=np.where((corr[1:-1]>corr[:-2])&(corr[1:-1]>=corr[2:]))[0]+1
            if len(peaks):
                best=max(corr[peaks]);valid=[i for i in peaks if corr[i]>=max(.65,best*.9)]
                if valid:i=valid[0];pitch=float(sr/lags[i]);conf=float(corr[i])
        frames.append(dict(time_s=round(start/sr,4),rms_dbfs=level,pitch_hz=pitch,pitch_confidence=conf))
    words=json.loads(Path(a.transcript).read_text());direction=json.loads(Path(a.direction).read_text());sections=[]
    for b in direction['sections']:
        fs=[z for z in frames if b['start_s']<=z['time_s']<b['end_s']];voiced=[z for z in fs if z['pitch_hz'] is not None];levels=[z['rms_dbfs'] for z in fs if z['rms_dbfs']>-32];ws=[z for z in words if b['start_s']<=z['start']<b['end_s']]
        pitch=[z['pitch_hz'] for z in voiced];item=dict(b,words=len(ws),words_per_minute=len(ws)/(b['end_s']-b['start_s'])*60,estimated_voiced_pitch_samples=len(voiced),voiced_rms_median_dbfs=float(np.median(levels)) if levels else None,voiced_rms_p10_p90_dbfs=[float(z) for z in np.percentile(levels,[10,90])] if levels else None)
        if pitch:
            item['pitch_median_hz']=float(np.median(pitch));item['pitch_p10_p90_hz']=[float(z) for z in np.percentile(pitch,[10,90])]
            item['pitch_span_semitones']=float(12*np.log2(item['pitch_p10_p90_hz'][1]/item['pitch_p10_p90_hz'][0]))
        sections.append(item)
    quiet=[];s=None
    for z in frames+[dict(time_s=len(x)/sr,rms_dbfs=0)]:
        if z['rms_dbfs']<-35 and s is None:s=z['time_s']
        elif z['rms_dbfs']>=-35 and s is not None:
            if z['time_s']-s>=.1:quiet.append(dict(start_s=s,end_s=z['time_s'],duration_s=round(z['time_s']-s,3)))
            s=None
    out=dict(voice_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),transcript_sha256=hashlib.sha256(Path(a.transcript).read_bytes()).hexdigest(),duration_s=len(x)/sr,sections=sections,quiet_gaps=quiet,frames=frames,limits='Profile of edited voice stem. ASR word times remain provisional. 60ms windows/50ms step; F0 80–444Hz with correlation>=0.65; octave/formant mistakes possible. RMS thresholds are local review presets. No hearing, emotion, interpretation or naturalness certified. Compare within this same speaker and validate intent against words/context.')
    Path(a.out).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(sections=sections,quiet_gaps=quiet),ensure_ascii=False))

if __name__=='__main__':main()
