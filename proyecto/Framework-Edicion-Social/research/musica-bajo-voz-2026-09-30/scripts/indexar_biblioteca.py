"""Índice editorial sin mover originales ni convertir usos puntuales en aprobación."""
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
FW = OUT.parents[1]
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def load(p):
    return json.loads((FW/p).read_text())


tracks = []
neon = load('library/music/candidates/2026-09-30-prueba-ritmica/manifest.json')
neon_path = FW/'library/music/candidates/2026-09-30-prueba-ritmica/neon-no-melody.mp3'
assert sha(neon_path) == neon['sha256']
preview = OUT/'audiciones/biblioteca-funciones/neon-20s.wav'
measure = subprocess.run([FF,'-hide_banner','-ss','45','-i',str(neon_path),'-t','20',
    '-af','loudnorm=I=-20:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,check=True)
log=measure.stderr.decode();stats=json.loads(log[log.rfind('{'):log.rfind('}')+1]);gain=-20-float(stats['input_i'])
subprocess.run([FF,'-v','error','-y','-ss','45','-i',str(neon_path),'-t','20','-af',
    f'volume={gain}dB,afade=t=in:d=0.1,afade=t=out:st=19.5:d=0.5',
    '-ar','48000','-ac','2','-c:a','pcm_s24le',str(preview)],check=True)
tracks.append({'id':neon['id'],'type':'bgm','title':'Neon · No Melody','file':str(neon_path.relative_to(FW)),
    'preview':str(preview.relative_to(FW)),'sha256':neon['sha256'],'preview_sha256':sha(preview),
    'preview_changes':{'source_start_s':45,'duration_s':20,'constant_gain_db':gain,'fade_in_s':.1,'fade_out_s':.5},
    'roles':['impulso','explicacion'],'character':'Pulso electrónico retro; descripción oficial y propuesta editorial.',
    'status':'direction_liked_in_C_pending_mix','feedback':'Te gustó el inicio y la dirección de C; pediste bajadas por momentos. No equivale a aprobación global.',
    'caution':'Arpegios pueden disputar palabras suaves; probar automatización por frase.',
    'license':neon['license'],'license_url':neon['license_url'],'credit':neon['credit'],'source_page':neon['source_page'],
    'source_manifest':'library/music/candidates/2026-09-30-prueba-ritmica/manifest.json','history':False})
for t in load('library/music/candidates/2026-09-30-funciones/manifest.json')['tracks']:
    tracks.append({'id':t['id'],'type':'bgm','title':t['title']+' · '+t['mix'],'file':t['file'],
        'preview':t['preview'],'sha256':t['sha256'],'preview_sha256':t['preview_sha256'],
        'preview_changes':t['preview_changes'],'roles':t['roles'],'character':t['description'],
        'status':'candidate_not_listened','feedback':'Pendiente de escuchar con voz real.',
        'caution':t['caution'],'license':t['license'],'license_url':t['license_url'],'credit':t['credit'],
        'source_page':t['source_page'],'source_manifest':'library/music/candidates/2026-09-30-funciones/manifest.json','history':False})
for t in load('library/music/candidates/2026-09-30/manifest.json')['tracks']:
    tracks.append({'id':t['id'],'type':'bgm','title':t['title']+' · '+t['mix'],
        'file':'library/music/candidates/2026-09-30/'+t['file'],
        'preview':t['preview'].removeprefix('Framework-Edicion-Social/'),'sha256':t['sha256'],
        'roles':['antecedente'],'character':t['fit'],'status':'presented_excerpt_rejected',
        'feedback':'Primera tanda descartada: demasiado calmada. Pista completa no evaluada globalmente.',
        'caution':'Conservar antecedente; no devolver automáticamente a la selección activa.',
        'license':t['license'],'license_url':t['license_url'],'credit':t['credit'],'source_page':t['source_page'],
        'source_manifest':'library/music/candidates/2026-09-30/manifest.json','history':True})
legacy = load('library/music/manifest.json')
path = FW/'library/music'/legacy['file']
tracks.append({'id':'BGM-ORIGINAL-TECH-PULSE','type':'bgm','title':'Pulso tecnológico original',
    'file':str(path.relative_to(FW)),'preview':str(path.relative_to(FW)),'sha256':sha(path),
    'roles':['antecedente'],'character':'Síntesis procedural discreta, 114 BPM.',
    'status':'legacy_context_review','feedback':'Antecedente del framework; encaje con la nueva dirección por confirmar.',
    'caution':'No asumir que una cama discreta resuelve la sensación plana.',
    'license':legacy['license'],'credit':'Original procedural synthesis; generate_bed.py · CC0-1.0.',
    'source_manifest':'library/music/manifest.json','history':True})
sfx_names = ['Entrada de aire','Transición suave','Tick puntual','Pop redondeado','Acento grave','Secuencia de tres','Regreso','Resolución']
roles = [['entrada'],['transicion'],['detalle'],['enfasis'],['contraste'],['secuencia'],['retorno'],['cierre']]
for i,t in enumerate(load('library/sfx/manifest.json')['files']):
    path=FW/'library/sfx'/t['file']
    tracks.append({'id':'SFX-ORIGINAL-'+t['file'].split('_')[0],'type':'sfx','title':sfx_names[i],
        'file':str(path.relative_to(FW)),'preview':str(path.relative_to(FW)),'sha256':sha(path),
        'roles':roles[i],'character':t['purpose'],'duration_s':t['duration_seconds'],
        'status':'existing_resource_context_review','feedback':'Recurso original; verificar ataque y cola en la mezcla de cada video.',
        'caution':'Nivel de fuente; ajustar contra la voz contemporánea. No es preset de volumen aprobado.',
        'license':t['license'],'credit':t['provenance']+' · CC0-1.0.',
        'source_manifest':'library/sfx/manifest.json','history':False})
catalog={'version':1,'date_local':'2026-09-30','short_video_rule':{'duration_s':[15,30],
    'music_count':'Una o dos según mensaje, duración y contexto; no cuota ni cambio por cronómetro.',
    'one_track':'Variar ganancia, arreglo, entradas, retiradas y acentos según voz y argumento.',
    'second_track':'Justificar con cambio de intención y revisar transición completa con voz.'},
    'tracks':tracks,'limits':['Roles propuestos, no clasificación emocional ni garantía de encaje.',
    'Aprobación se registra por recurso/tramo/mezcla; feedback de C no aprueba el catálogo completo.',
    'Ninguna música extraída de las referencias se incorpora a esta biblioteca.']}
# Preserve expanded catalog and user feedback when regenerating the original index.
existing_path = FW/'library/music/catalogo-editorial.json'
if existing_path.exists():
    existing = json.loads(existing_path.read_text())
    old_by_id = {t['id']:t for t in existing.get('tracks',[])}
    for t in catalog['tracks']:
        previous = old_by_id.get(t['id'],{})
        for key in ['status','feedback','feedback_history','context_bank']:
            if key in previous: t[key] = previous[key]
    ids = {t['id'] for t in catalog['tracks']}
    catalog['tracks'].extend(t for t in existing.get('tracks',[]) if t['id'] not in ids)
    if 'feedback_history' in existing: catalog['feedback_history'] = existing['feedback_history']
existing_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'music_active':sum(t['type']=='bgm' and not t['history'] for t in catalog['tracks']),'music_history':sum(t['history'] for t in catalog['tracks']),'sfx':sum(t['type']=='sfx' for t in catalog['tracks']),'catalog':str(FW/'library/music/catalogo-editorial.json')},ensure_ascii=False))
