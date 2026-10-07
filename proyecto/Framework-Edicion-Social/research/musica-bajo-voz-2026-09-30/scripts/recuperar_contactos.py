"""Recupera únicamente las capturas fallidas, reutilizando metadatos y mediciones."""
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1]
EVIDENCE = OUT / 'evidencia'
path = EVIDENCE / 'revision-existentes.json'
records = json.loads(path.read_text())
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
sheets = {}
for r in records:
    if not r.get('render'): continue
    imgs=[]
    if r.get('capture_errors'):
        r['capture_errors_initial'] = r.pop('capture_errors')
    hdr = any(s.get('color_transfer') in ['arib-std-b67','smpte2084'] for s in r['streams'])
    vf = 'scale=180:-2'
    if hdr:
        vf = 'zscale=t=linear:npl=100,format=gbrpf32le,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale=180:-2'
    for ratio in [0.25,0.70]:
        frame = EVIDENCE / f"{r['id']}-{ratio:.2f}.jpg"
        sec=round(r['duration_s']*ratio,3)
        if not frame.exists() or frame.stat().st_size == 0:
            args=['/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg','-hide_banner','-loglevel','error','-ss',str(sec),'-i',str(ROOT/r['render']),'-frames:v','1','-vf',vf,'-y',str(frame)]
            p=subprocess.run(args,capture_output=True,text=True,timeout=90)
            if p.returncode: raise RuntimeError(p.stderr)
        imgs.append((r['id'],sec,frame))
    r['sample_frames']=[str(p.relative_to(OUT)) for _,_,p in imgs]
    r['capture_status']='pass'
    sheets.setdefault(r['group'],[]).extend(imgs)
for group,items in sheets.items():
    cols=5 if group=='01-10' else 4
    canvas=Image.new('RGB',(cols*200,((len(items)+cols-1)//cols)*355),(22,25,30))
    draw=ImageDraw.Draw(canvas)
    for i,(label,sec,frame) in enumerate(items):
        x,y=(i%cols)*200+10,(i//cols)*355+26
        img=Image.open(frame).convert('RGB'); img.thumbnail((180,320)); canvas.paste(img,(x,y))
        draw.text((x,y-21),f'{label}  {sec:.2f}s',fill='white',font=font)
    canvas.save(EVIDENCE/f'contacto-{group}.jpg',quality=92)
path.write_text(json.dumps(records,ensure_ascii=False,indent=2))
print('Recuperadas las capturas; tres láminas,',sum(map(len,sheets.values())),'fotogramas.')
