"""Verifica archivos de investigación y preservación de renders muestreados."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parents[1]
BANK=ROOT/'Framework-Edicion-Social/library/music/candidates/2026-09-30'
issues=[]

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

rows=json.loads((OUT/'evidencia/revision-existentes.json').read_text())
for r in rows:
 if sha(ROOT/r['render'])!=r['render_sha256']:issues.append('Render cambió durante investigación: '+r['id'])
 if len(r['sample_frames'])!=2:issues.append('Faltan muestras: '+r['id'])
tracks=json.loads((BANK/'manifest.json').read_text())['tracks']
for t in tracks:
 if sha(ROOT/t['download_path'])!=t['sha256']:issues.append('Hash candidato: '+t['title'])
 if t['license']!='CC BY 4.0' or t['decode_full']!='pass':issues.append('Licencia o decode: '+t['title'])
for s in re.findall(r'(?:href|src)="([^"]+)"',(OUT/'banco.html').read_text()):
 if s.startswith(('http:','https:','#')):continue
 if not (OUT/unquote(s)).resolve().exists():issues.append('Enlace roto: '+s)
auditions=[]
for p in sorted((OUT/'audiciones').iterdir()):
 if not p.is_file():continue
 probe=subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)],capture_output=True,text=True)
 decode=subprocess.run(['/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg','-v','error','-i',str(p),'-f','null','-'],capture_output=True,text=True)
 if probe.returncode or decode.returncode:issues.append('Probe o decode: '+p.name);continue
 d=json.loads(probe.stdout); dur=float(d['format']['duration'])
 expected=20 if 'musica-sola' in p.name else 12
 if abs(dur-expected)>0.2:issues.append('Duración: '+p.name)
 auditions.append({'file':p.name,'duration_s':dur,'sha256':sha(p),'decode_full':'pass'})
result={'status':'pass' if not issues else 'needs_review','date_local':'2026-09-30',
        'render_hashes_unchanged':len(rows)-sum('Render cambió' in x for x in issues),
        'renders_sampled':len(rows),'frames_inspected':sum(len(r['sample_frames']) for r in rows),
        'downloaded_tracks':len(tracks),'html_local_links':'pass' if not any('Enlace roto' in x for x in issues) else 'fail',
        'audition_files':auditions,'issues':issues,
        'human_listening':'por confirmar','audience_results':'awaiting_data',
        'browser_check':'Página inspeccionada en captura; carga de reproductor de voz verificada en UI, sin afirmar escucha.'}
feedback_path=OUT/'evidencia/feedback-usuario.json'
if feedback_path.exists():
 feedback=json.loads(feedback_path.read_text())
 result['human_listening']='Feedback de rechazo de la tanda y voz sola plana reportado por el usuario; escucha completa por confirmar.'
 result['feedback_reference']='feedback-usuario.json'
(OUT/'evidencia/validacion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='audition_files'},ensure_ascii=False,indent=2))
if issues:raise SystemExit(1)
