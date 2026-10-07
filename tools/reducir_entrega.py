"""One-time, scoped reduction of the already-created delivery. Never visits Mac sources."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT/'proyecto'
FRAMEWORK = PROJECT/'Framework-Edicion-Social'
SERIES = PROJECT/'Serie-IA-Negocios-10-Videos'
TEXT = {'.md','.json','.jsonl','.csv','.txt','.py','.log','.sha256','.yaml','.yml'}


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply',action='store_true')
    args=ap.parse_args()
    if not (ROOT/'evidencia/historico-v1/configuracion-antes-ligera.zip').is_file():
        raise RuntimeError('Original delivery metadata must be preserved first')
    projects=json.loads((ROOT/'proyectos.json').read_text())
    if len(projects)!=30 or any(p['video']>30 for p in projects):
        raise RuntimeError('Only the untouched initial 30-project delivery can be reduced')
    all_before=[p for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink()]
    before=sum(p.stat().st_size for p in all_before)
    previews=set()
    for track in json.loads((FRAMEWORK/'library/music/catalogo-editorial.json').read_text())['tracks']:
        for key in ('file','preview','source_manifest'):
            if track.get(key):previews.add((FRAMEWORK/track[key]).resolve())
    def keep(p):
        relative=p.relative_to(PROJECT)
        parts=relative.parts
        if parts[0]=='Framework-Edicion-Social':
            if '__pycache__' in parts or p.suffix in {'.pyc','.lock'}:return False
            if len(parts)>1 and parts[1]=='research':
                return p.suffix.lower() in TEXT or p.resolve() in previews
            return True
        if parts[0]=='Serie-IA-Negocios-10-Videos':
            return len(parts)>1 and parts[1] in {'PROPUESTAS-ESTRUCTURA','scripts'} and '__pycache__' not in parts
        return relative.as_posix() in {'AGENTS.md','BITACORA_CURSO_EDICION.md'}
    delete=[p for p in PROJECT.rglob('*') if p.is_file() and not keep(p)]
    # Generated diagnostics can contain an old full voice/mix too.
    delete += [p for p in (ROOT/'evidencia').rglob('*') if p.is_file() and p.suffix.lower() in {'.wav','.mp4','.mov','.m4a','.png','.jpg'}]
    delete += [p for p in (ROOT/'resultados').rglob('*') if p.is_file()]
    print(json.dumps({'before_MB':round(before/1e6,2),'files_to_remove':len(delete),
                      'bytes_to_remove':sum(p.stat().st_size for p in delete)}),flush=True)
    if not args.apply:return
    if (PROJECT/'plantillas-codigo').exists():raise RuntimeError('Template extraction already exists; do not overwrite')
    templates=[];resources={}
    for row in projects:
        old=PROJECT/row['path']; target=PROJECT/'plantillas-codigo'/f'T{row["video"]:02d}'
        target.mkdir(parents=True)
        source_rows=[]
        # Archive only composition source, not full old editing projects or media.
        candidates=list(old.glob('*.html'))+list((old/'compositions').rglob('*.html'))
        candidates += [p for p in old.rglob('*') if p.is_file() and p.suffix in {'.css','.js'} and not any(s in p.parts for s in ('qa','renders','snapshots'))]
        for p in sorted(set(candidates)):
            rel=p.relative_to(old)
            out=target/(rel.as_posix()+'.referencia')
            out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
            source_rows.append({'file':out.relative_to(PROJECT).as_posix(),'source_path':p.relative_to(PROJECT).as_posix(),'sha256':sha(p)})
        # Fonts and SVG are code/native reusable resources; keep origin and deduplicate by bytes.
        for p in old.rglob('*'):
            if not p.is_file() or p.suffix.lower() not in {'.svg','.woff','.woff2','.ttf','.otf'}:continue
            if any(s in p.parts for s in ('qa','renders','snapshots')):continue
            digest=sha(p);key=digest+p.suffix.lower()
            out=PROJECT/'recursos-reutilizables'/key
            if key not in resources:
                out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
                resources[key]={'file':out.relative_to(PROJECT).as_posix(),'sha256':digest,'origins':[],
                                'reuse':'Conserve source/licence and check semantic fit; not globally approved by extraction.'}
            resources[key]['origins'].append(p.relative_to(PROJECT).as_posix())
        templates.append({'id':f'T{row["video"]:02d}','path':target.relative_to(PROJECT).as_posix(),
                          'hyperframes_reference':row['hyperframes'],'files':source_rows,
                          'status':'source_reference_requires_new_media_and_timing','video_approval_transferred':False})
    save(PROJECT/'plantillas-codigo/catalogo.json',{'templates':templates})
    save(PROJECT/'recursos-reutilizables/catalogo.json',{'resources':list(resources.values())})
    # Retain original approval history separately; the active package represents source recipes only.
    registry=FRAMEWORK/'template-bank/registry.json'
    shutil.copy2(registry,ROOT/'evidencia/historico-v1/template-bank-original.json')
    bank=json.loads(registry.read_text());bank['updated_at']='2026-10-06'
    for i,row in enumerate(bank['templates'],1):
        row['version']=row['version'].split('-')[0]+'-windows-source'
        row['source_project']=f'plantillas-codigo/T{i:02d}'
        row['status']='candidate'
        row['artifact_approval']={'video_id':None,'status':'not_applicable','receipt_path':None,'scope':None,
             'reason':'Lightweight code reference only. Original artifact decision is retained in evidencia/historico-v1/template-bank-original.json, outside the active registry.'}
        row['template_reuse']={'status':'pending','scope':None,'authorization_basis':'none','authorization_ref':None,
             'evidence_video_ids':[],'reason':'No render approval inherited. Design proposals retain their separate documented approval.'}
    save(registry,bank)
    styles=FRAMEWORK/'styles/catalog.json'
    shutil.copy2(styles,ROOT/'evidencia/historico-v1/styles-catalog-original.json')
    data=json.loads(styles.read_text())
    for row in data['styles']:
        row.pop('validated_preview',None);row.pop('implementation',None)
    save(styles,data)
    removed=[]
    for p in delete:
        if p.is_symlink() or not p.resolve().is_relative_to(ROOT):raise RuntimeError('Refuse deletion outside kit: '+str(p))
        removed.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
        p.unlink()
    for folder in sorted(PROJECT.rglob('*'),key=lambda p:len(p.parts),reverse=True):
        if folder.is_dir() and not any(folder.iterdir()):folder.rmdir()
    save(ROOT/'proyectos.json',[])
    save(ROOT/'kit-config.json',{'edition':'light','version':'1.1.0','hyperframes':'0.8.102',
         'first_new_video':31,'templates':'proyecto/Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/CATALOGO_MAESTRO_01_A_30.json',
         'windows_verified':False})
    save(ROOT/'evidencia/reduccion-2026-10-06.json',{'before_bytes':before,'removed':removed,
         'mac_source_modified':False,'reason':'Explicit request to remove prior video work from this existing delivery, retaining framework/templates/resources.',
         'template_sources':len(templates),'deduplicated_svg_fonts':len(resources)})
    print(json.dumps({'removed_files':len(removed),'removed_bytes':sum(x['bytes']for x in removed),
                      'template_sources':len(templates),'reusable_svg_fonts':len(resources)}),flush=True)


if __name__=='__main__':main()
