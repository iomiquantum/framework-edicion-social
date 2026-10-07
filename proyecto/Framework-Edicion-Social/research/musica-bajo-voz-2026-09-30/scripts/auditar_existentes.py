"""Inventario de renders y muestreo visual; no modifica composiciones ni medios fuente."""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
FFMPEG = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
OUT = Path(__file__).resolve().parents[1]
EVIDENCE = OUT / 'evidencia'
EVIDENCE.mkdir(parents=True, exist_ok=True)
EXCLUDE = {'node_modules', '.git', 'assets', 'source', 'input', 'media',
           '00-INGESTA', '__pycache__', '.hyperframes', '.transcode-cache',
           'voice-lab', 'voice-lab-generic', 'frames', 'snapshots'}

def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=100)

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

inventory = []
for d, dirs, files in os.walk(ROOT):
    dirs[:] = [x for x in dirs if x not in EXCLUDE and not x.startswith('.')
               and not x.startswith('qa') and not x.startswith('work-')]
    for fn in files:
        p = Path(d) / fn
        if p.suffix.lower() in {'.mp4', '.mov', '.webm'}:
            # Fuentes y proxies no constituyen renders editoriales.
            if any(s in fn.lower() for s in ['proxy', 'raw_', 'original', 'video-only', 'master']):
                continue
            if 'research/musica-bajo-voz-' in str(p):
                continue
            inventory.append({'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size})
(EVIDENCE / 'inventario-renders.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2))

specs = []
for n in list(range(1, 17)) + [21, 22]:
    base = ROOT / 'Serie-IA-Negocios-10-Videos' / f'VIDEO-{n:02d}'
    project = base / f'editable-hyperframes-video-{n:02d}'
    if n <= 10:
        candidates = list(base.glob(f'VIDEO-{n:02d}_REVISION_v*.mp4'))
        video = max(candidates, key=lambda p: int(re.search(r'_v(\d+)', p.name)[1])) if candidates else None
    elif n <= 15:
        video = project / 'renders' / f'VIDEO-{n:02d}-FINAL.mp4'
    elif n == 16:
        video = base / 'VIDEO-16-PARA-APROBACION-v4.mp4'
    elif n == 21:
        video = project / 'renders' / 'VIDEO-21-ENTREGA-HLG-v2.mp4'
    else:
        video = base / 'entrega' / 'VIDEO-22-ENTREGA-HLG-v2-audio-conservado.mp4'
    specs.append((f'VIDEO-{n:02d}', project, video, '01-10' if n <= 10 else '11-22'))

extras = [
 ('MIGUEL-PILOTO', 'Miguel-Reel-Piloto/editables/hyperframes-piloto', 'Miguel-Reel-Piloto/outputs/MIGUEL_REEL_PILOTO_FASE2.mp4'),
 ('MIGUEL-V2', 'Miguel-Reel-Piloto/editables/hyperframes-full-v2', 'Miguel-Reel-Piloto/outputs/MIGUEL_REEL_COMPLETO_PRO_V2.mp4'),
 ('WELLNESS', 'WhatsApp-Reel-Prueba-Fuego/editables/hyperframes-wellness-v1', 'WhatsApp-Reel-Prueba-Fuego/outputs/PRUEBA_FUEGO_IMMERSIVE_WELLNESS_V1.mp4'),
 ('EXPLAINER-V1', 'NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/videos/retrabajo-acelerado', 'NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/videos/retrabajo-acelerado/renders/video-delivery.mp4'),
 ('EXPLAINER-V2', 'NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/videos/retrabajo-acelerado-v2', 'NUEVO-EXPLAINER-HYPERFRAMES-2026-09-26/videos/retrabajo-acelerado-v2/renders/video-v2-delivery.mp4'),
 ('MUSE-06', 'PRUEBAS-MUSE/VIDEO-06-VARIANTE-01/editable-hyperframes-video-06', 'PRUEBAS-MUSE/VIDEO-06-VARIANTE-01/VIDEO-06_REVISION_v3.mp4'),
 ('MUSE-12', 'PRUEBAS-MUSE/VIDEO-12-EDICION-01/editable-video12-v4', 'PRUEBAS-MUSE/VIDEO-12-EDICION-01/VIDEO-12_MUSE_V4.mp4'),
 ('MUSE-14', 'PRUEBAS-MUSE/VIDEO-14-EDICION-01/editable-video14', 'PRUEBAS-MUSE/VIDEO-14-EDICION-01/VIDEO-14_MUSE_V1.mp4'),
]
specs += [(name, ROOT/p, ROOT/v, 'otras-familias') for name, p, v in extras]
records = []
sheets = {}
for label, project, video, group in specs:
    rec = {'id': label, 'project': str(project.relative_to(ROOT)), 'visual_review': 'pending',
           'human_listening': 'por confirmar', 'group': group}
    if (project / 'index.html').exists():
        timeline = run(['npx', '--yes', 'hyperframes@0.8.99', 'timeline', '--json'], cwd=project)
        (EVIDENCE / f'{label}-timeline.json').write_text(timeline.stdout)
        if timeline.returncode == 0:
            try:
                t = json.loads(timeline.stdout)['timeline']
                rows = [r for track in t['tracks'] for r in track.get('rows', [])]
                rec['timeline_duration_s'] = t['duration']
                rec['audio_layers'] = [{k:r.get(k) for k in ['id','src','volume','audioGroup','role','absStart','absEnd']}
                                       for r in rows if r.get('kind') == 'audio']
            except (KeyError, ValueError) as e:
                rec['timeline_error'] = str(e)
        else:
            rec['timeline_error'] = timeline.stderr[-1000:]
    if video and video.exists():
        rec['render'] = str(video.relative_to(ROOT))
        rec['render_sha256'] = sha(video)
        probe = run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)])
        data = json.loads(probe.stdout)
        (EVIDENCE / f'{label}-probe.json').write_text(probe.stdout)
        dur = float(data['format']['duration'])
        rec['duration_s'] = dur
        rec['streams'] = [{k:s.get(k) for k in ['codec_type','codec_name','width','height','r_frame_rate','sample_rate','channels','color_transfer']}
                          for s in data['streams']]
        # Medición del programa completo; no atribuye nivel a voz o música aislada.
        measure = run(['ffmpeg','-hide_banner','-nostats','-i',str(video),'-vn','-af',
                       'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
        (EVIDENCE / f'{label}-loudness.log').write_text(measure.stderr)
        blobs = re.findall(r'\{\s*"input_i".*?\}', measure.stderr, re.S)
        if blobs:
            rec['program_loudness'] = json.loads(blobs[-1])
        imgs=[]
        for ratio in [0.25, 0.70]:
            sec = round(dur * ratio, 3)
            frame = EVIDENCE / f'{label}-{ratio:.2f}.jpg'
            vf = 'scale=180:-2'
            hdr = any(s.get('color_transfer') in ['arib-std-b67','smpte2084'] for s in data['streams'])
            if hdr:
                vf = 'zscale=t=linear:npl=100,format=gbrpf32le,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale=180:-2'
            capture = run([FFMPEG,'-hide_banner','-loglevel','error','-ss',str(sec),'-i',str(video),'-frames:v','1','-vf',vf,'-y',str(frame)])
            if capture.returncode == 0:
                imgs.append((label,sec,frame))
            else:
                rec.setdefault('capture_errors',[]).append(capture.stderr[-600:])
        rec['sample_frames'] = [str(f.relative_to(OUT)) for _,_,f in imgs]
        sheets.setdefault(group,[]).extend(imgs)
    else:
        rec['missing_render'] = str(video) if video else True
    records.append(rec)
    (EVIDENCE / 'revision-existentes.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
    print(label, 'ok' if rec.get('render') else 'sin render', flush=True)

font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14)
for group, items in sheets.items():
    if not items:
        print('Sin muestras capturadas:',group,flush=True)
        continue
    cols = 5 if group == '01-10' else 4
    width, height = cols*200, ((len(items)+cols-1)//cols)*355
    canvas = Image.new('RGB',(width,height),(22,25,30))
    draw = ImageDraw.Draw(canvas)
    for i,(label,sec,frame) in enumerate(items):
        x,y = (i%cols)*200+10,(i//cols)*355+26
        img = Image.open(frame).convert('RGB')
        img.thumbnail((180,320))
        canvas.paste(img,(x,y))
        draw.text((x,y-21),f'{label}  {sec:.2f}s',fill='white',font=font)
    canvas.save(EVIDENCE / f'contacto-{group}.jpg',quality=92)
print('Inventario',len(inventory),'renders; muestras',len(records),flush=True)
