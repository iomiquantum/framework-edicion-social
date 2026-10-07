"""Compara voz y camas servidas. Energía de banda no diagnostica atención subjetiva."""
import concurrent.futures
import json
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parents[1]
FFMPEG='/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
data=json.loads((OUT/'evidencia/audiciones.json').read_text())
bands=[200,630,1600,4000]
tasks=[('voz',ROOT/data['voice_clip'],1,False,f) for f in bands]
for mix in data['mixes']:
 bed=OUT/'audiciones'/f"{mix['name']}-cama-12s.wav"
 tasks += [(mix['name'],bed,mix['music_gain'],True,f) for f in bands]

def measure(task):
 name,p,gain,fade,f=task
 filt=f'volume={gain:.12f},'
 if fade:filt+='afade=t=in:st=0:d=0.35,afade=t=out:st=11:d=1,'
 filt+=f'bandpass=f={f}:width_type=h:w={f*0.2316},volumedetect'
 proc=subprocess.run([FFMPEG,'-hide_banner','-nostats','-i',str(p),'-af',filt,'-f','null','-'],capture_output=True,text=True,timeout=50)
 if proc.returncode:raise RuntimeError(proc.stderr)
 level=float(re.search(r'mean_volume: ([-\d.]+) dB',proc.stderr)[1])
 return {'track':name,'center_hz':f,'bandwidth_hz':f*0.2316,'mean_dbfs':level}

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 results=list(pool.map(measure,tasks))
voice={x['center_hz']:x['mean_dbfs'] for x in results if x['track']=='voz'}
for r in results:
 if r['track']!='voz':r['voice_minus_music_db']=round(voice[r['center_hz']]-r['mean_dbfs'],1)
evidence={'date_local':'2026-09-30','method':'FFmpeg bandpass de tercio de octava y volumedetect sobre fragmentos exactos, con ganancia/fundidos de cama iguales a audición. Media de doce segundos; no análisis de palabra ni prueba perceptual.',
          'results':results,'limit':'Ni una forma espectral ni LUFS identifican por sí solos la causa de desatención. No diagnosticar un filtro de voz sin referencia. No se alteró el sonido.'}
(OUT/'evidencia/comparacion-bandas.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
for r in results:
 if r['track']!='voz':print(r['track'],r['center_hz'],'Hz, voz sobre cama:',r['voice_minus_music_db'],'dB')
