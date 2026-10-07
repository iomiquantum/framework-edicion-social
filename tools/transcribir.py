"""Offline-capable ASR. Model download is a separate explicitly approved setup action."""
import argparse, hashlib, json, os, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--source');p.add_argument('--out');p.add_argument('--language',default='es');a=p.parse_args()
from faster_whisper import WhisperModel
model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=2,download_root=str(ROOT/'runtime/models/whisper-small'),local_files_only=True)
if a.check:
 print('Whisper small multilingüe cargado sin descarga; CPU int8');sys.exit(0)
if not a.source or not a.out:p.error('--source y --out requeridos')
src=Path(a.source).resolve();out=Path(a.out).resolve()
if out.exists():raise SystemExit('La transcripción ya existe; reutilízala o elige otra ruta.')
started=time.monotonic();digest=hashlib.sha256()
with src.open('rb') as f:
 for block in iter(lambda:f.read(4*1024*1024),b''):digest.update(block)
segments,info=model.transcribe(str(src),language=a.language,word_timestamps=True)
rows=[];words=[]
for s in segments:
 rows.append({'start':s.start,'end':s.end,'text':s.text})
 words.extend({'start':w.start,'end':w.end,'text':w.word} for w in (s.words or []))
data={'source':str(src),'sha256':digest.hexdigest(),'model':'small','language':info.language,'segments':rows,'words':words,'human_review':'pending','seconds':round(time.monotonic()-started,2)}
out.parent.mkdir(parents=True,exist_ok=True)
with out.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
print(str(out))
