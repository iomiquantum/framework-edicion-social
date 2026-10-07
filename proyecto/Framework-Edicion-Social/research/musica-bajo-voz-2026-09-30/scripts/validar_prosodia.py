"""Comprueba inputs, audiciones finales y enlaces; no aprueba interpretación."""
from pathlib import Path
import hashlib, json, re, subprocess
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parents[1]
data=json.loads((OUT/'evidencia/prosodia/analisis.json').read_text())
issues=[]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
checks=[]
for p in data['pieces']:
 if sha(ROOT/p['project']/'index.html')!=p['html_sha256']:issues.append('HTML cambió: '+p['id'])
 for a in p['inputs']:
  if sha(ROOT/a['path'])!=a['sha256']:issues.append('Fuente cambió: '+a['path'])
 for c in p.get('cues',[]):
  if not 0<=c['start']<c['end']<=p['metrics']['duration_s']+.1:issues.append('Cue inválido: '+p['id'])
for a in data['auditions']:
 path=OUT/a['file']
 if sha(path)!=a['sha256']:issues.append('Audición cambió: '+a['id'])
 probe=subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)],capture_output=True,text=True,check=True)
 meta=json.loads(probe.stdout); stream=meta['streams'][0]
 decode=subprocess.run(['/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg','-v','error','-i',str(path),'-f','null','-'],capture_output=True,text=True)
 if decode.returncode:issues.append('Decode: '+a['id'])
 if stream['sample_rate']!='48000' or stream['codec_name']!='pcm_s24le':issues.append('Formato: '+a['id'])
 expected=data['origin_video13']['metrics']['duration_s'] if a['id']=='VIDEO-13-ORIGEN' else next(p['metrics']['duration_s'] for p in data['pieces'] if p['id']==a['id'])
 if abs(float(meta['format']['duration'])-expected)>.01:issues.append('Duración: '+a['id'])
 if abs(a['lufs']+22)>.1 or a['true_peak_db']>-1:issues.append('Nivel: '+a['id'])
 checks.append({'id':a['id'],'duration_s':float(meta['format']['duration']),'lufs':a['lufs'],'true_peak_db':a['true_peak_db'],'decode':'pass' if not decode.returncode else 'fail','sha256':a['sha256']})
for name in ['voz.html','banco.html']:
 for link in re.findall(r'(?:href|src)="([^"]+)"',(OUT/name).read_text()):
  if not link.startswith(('http:','https:','#')) and not (OUT/link).resolve().exists():issues.append('Enlace roto: '+link)
result={'status':'pass' if not issues else 'needs_review','pieces':len(data['pieces']),'phrase_maps':sum(bool(p.get('cues')) for p in data['pieces']),'phrases':sum(len(p.get('cues',[])) for p in data['pieces']),'source_voice_hashes':'pass' if not any('Fuente cambió' in s for s in issues) else 'fail','auditions':checks,'issues':issues,'perceptual_interpretation':'por confirmar','existing_videos_modified':False}
(OUT/'evidencia/prosodia/validacion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
if issues:raise SystemExit(1)
