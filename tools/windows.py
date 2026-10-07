"""Isolated portable entry point. Does not discover or write into the Mac source."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
import portable_fcntl

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def project(number):
    item = next((p for p in read(ROOT/'proyectos.json') if p['video'] == number), None)
    if item is None:
        raise ValueError('Video absent from this snapshot')
    path = (ROOT/'proyecto'/item['path']).resolve()
    if not path.is_relative_to((ROOT/'proyecto').resolve()):
        raise ValueError('Project outside the isolated snapshot')
    settings = path.parent/'windows-project.json'
    if settings.is_file():
        local = read(settings)
        if local.get('video') != number or local.get('hyperframes') != item['hyperframes']:
            raise ValueError('Project settings disagree with project registry')
        hook = local.get('hook_end')
        if hook is not None and (isinstance(hook, bool) or not isinstance(hook, (float, int)) or not math.isfinite(hook) or hook <= 0):
            raise ValueError('hook_end must be a positive finite number, or null until planned')
        transfer = local.get('delivery_transfer')
        if transfer not in ('bt709', 'arib-std-b67'):
            raise ValueError('Set an explicit supported delivery colour transfer')
        item = {**item, 'hook_end':hook, 'delivery_transfer':transfer,
                'sfx_plan_present':(path/'qa/sfx-calibration.json').is_file()}
    return item, path


def new_project(number, template_id):
    if not 1 <= number <= 9999:
        raise ValueError('Video number must be between 1 and 9999')
    config = read(ROOT/'kit-config.json')
    runtime_settings=read(ROOT/'runtime.local.json') if (ROOT/'runtime.local.json').is_file() else {}
    config['hyperframes']=runtime_settings.get('hyperframes',config['hyperframes'])
    catalog_path = ROOT/config['templates']
    catalog = read(catalog_path)
    selected = next((t for t in catalog['templates'] if t['id'] == template_id), None)
    if selected is None:
        raise ValueError('Choose a template from T01 to T30')
    with machine_lock():
        records = read(ROOT/'proyectos.json')
        parent = ROOT/'proyecto'/'Nuevos-Videos'/f'VIDEO-{number:02d}'
        if parent.exists() or any(r['video'] == number for r in records):
            raise ValueError('Video already exists; previous work will not be overwritten')
        parent.mkdir(parents=True)
        for folder in ('source','editable/assets','editable/qa','entregas'):
            (parent/folder).mkdir(parents=True)
        item = {'video':number, 'path':(parent/'editable').relative_to(ROOT/'proyecto').as_posix(),
                'hyperframes':config['hyperframes'], 'template':template_id, 'hook_end':None,
                'delivery_transfer':'bt709', 'sfx_plan_present':False,'windows_runtime_verified':False}
        save(parent/'windows-project.json',item)
        save(parent/'PLANTILLA_SELECCIONADA.json',{
            'selection':selected,'catalog_path':config['templates'],
            'catalog_sha256':hashlib.sha256(catalog_path.read_bytes()).hexdigest(),
            'code_reference':f'plantillas-codigo/{template_id}',
            'flow':1,'new_video_approved':False,
            'stage':'Preparation only; read current rules, map the real voice and review template fidelity before composing.'})
        fidelity = ROOT/'proyecto/Framework-Edicion-Social/templates/template-fidelity-review.md'
        shutil.copy2(fidelity,parent/'QA_FIDELIDAD_PLANTILLA.md')
        (parent/'LEEME.md').write_text(
            f'# VIDEO-{number:02d}: {selected["name"]}\n\n'
            'Coloca la nueva grabación en source/. Consulta AGENTS.md, la bitácora, '
            'las reglas del framework, la ficha/tablero elegidos y la referencia de código. '
            'Guarda el recibo de inicio con los documentos realmente consultados. '
            'Reutiliza ingesta/ASR del lote cuando existan. Realiza la maqueta y revisión '
            'de fidelidad antes de construir editable/index.html.\n\n'
            'Esta carpeta no contiene una composición ni una aprobación. '
            'Después del montaje, declara el hook real en windows-project.json, '
            'conserva el plan SFX verificable y ejecuta los controles habituales. '
            'BT.709 es el valor inicial de entrega, no una conversión aplicada al original.\n',encoding='utf-8')
        temporary = ROOT/'proyectos.next.json'
        save(temporary,records+[item])
        temporary.replace(ROOT/'proyectos.json')
    print(json.dumps({'project':str(parent),'template':selected['name'],'stage':'prepared_not_composed'},ensure_ascii=False,indent=2))


def execute(command, cwd=None, env=None, capture=False):
    result = subprocess.run([str(x) for x in command], cwd=cwd, env=env,
                            capture_output=capture, text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError(f'Command failed ({result.returncode}): {command[0]}\n'+(result.stderr or ''))
    return result.stdout or ''


def runtime():
    config_file = ROOT/'runtime.local.json'
    config = read(config_file) if config_file.exists() else {}
    found = {}
    for tool in ('node', 'ffmpeg', 'ffprobe'):
        found[tool] = (config.get(tool) if config.get(tool) and Path(config[tool]).is_file() else None) or shutil.which(tool)
        if not found[tool] or not Path(found[tool]).is_file():
            raise RuntimeError(f'Missing {tool}. Run setup.ps1 on Windows; see LEEME.md.')
    # Existing SFX guard resolves the sibling ffprobe; require that same binary.
    sibling = Path(found['ffmpeg']).with_name('ffprobe.exe' if os.name == 'nt' else 'ffprobe')
    if not sibling.is_file() or sibling.resolve() != Path(found['ffprobe']).resolve():
        raise RuntimeError('ffmpeg and ffprobe must be from the same installation directory')
    return found


def cli(item, config):
    package_dir = ROOT/'runtime'/'hyperframes'/item['hyperframes']/'node_modules'/'hyperframes'
    metadata = read(package_dir/'package.json')
    if metadata['version'] != item['hyperframes']:
        raise RuntimeError('HyperFrames version mismatch; rerun setup with this video')
    entry = metadata['bin']
    if isinstance(entry, dict):
        entry = entry['hyperframes']
    path = (package_dir/entry).resolve()
    if not path.is_relative_to(package_dir.resolve()) or not path.is_file():
        raise RuntimeError('Invalid local HyperFrames entry point')
    return [config['node'], str(path)]


def environment(config):
    env = dict(os.environ)
    env.update(HYPERFRAMES_FFMPEG_PATH=config['ffmpeg'], HYPERFRAMES_FFPROBE_PATH=config['ffprobe'],
               HYPERFRAMES_NO_UPDATE_CHECK='1', PYTHONUTF8='1',
               HYPERFRAMES_EXTRACT_CACHE_DIR=str(ROOT/'runtime'/'frames-cache'))
    env['PATH'] = os.pathsep.join([str(Path(config['ffmpeg']).parent), env.get('PATH', '')])
    return env


@contextmanager
def machine_lock():
    path = ROOT/'runtime'/'heavy-job.lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as handle:
        try:
            portable_fcntl.flock(handle, portable_fcntl.LOCK_EX | portable_fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError('Another heavy job is running in this local kit') from error
        try:
            yield
        finally:
            portable_fcntl.flock(handle, portable_fcntl.LOCK_UN)


def preflight(item, path, config, output):
    scripts = ROOT/'proyecto'/'Framework-Edicion-Social'/'scripts'
    env = environment(config)
    execute([sys.executable, scripts/'validar_texto_visible.py', '--project', path,
             '--report', output/'visible-text.json'], env=env)
    # A historical approval does not fabricate a portable SFX plan or hook boundary.
    if not (path/'qa/sfx-calibration.json').is_file() or item.get('hook_end') is None:
        raise RuntimeError('SFX plan or contextual hook missing. This legacy editable needs a documented port before rendering.')
    execute([sys.executable, scripts/'revisar_presencia_sfx.py', '--project', path,
             '--ffmpeg', config['ffmpeg'], '--out', output/'sfx', '--hook-end', str(item['hook_end'])], env=env)


def doctor(output):
    config = runtime()
    versions = {k: execute([v, '--version' if k == 'node' else '-version'], capture=True).splitlines()[0]
                for k, v in config.items()}
    node_major = int(re.search(r'(\d+)\.', versions['node']).group(1))
    if node_major < 22 or sys.version_info < (3, 11):
        raise RuntimeError('Requires Node >=22 and Python >=3.11')
    filters = execute([config['ffmpeg'], '-hide_banner', '-filters'], capture=True)
    missing = [x for x in ('zscale', 'tonemap', 'loudnorm') if not re.search(r'\b'+x+r'\b', filters)]
    if missing:
        raise RuntimeError('FFmpeg build lacks '+', '.join(missing))
    with machine_lock():
        pass
    result = {'status':'pass', 'platform':platform.platform(), 'python':sys.version,
              'tools':config, 'versions':versions, 'filters':['zscale','tonemap','loudnorm'],
              'limits':'Dependency check only. Does not certify Chrome rendering, Windows parity, audio model calibration or video approval.'}
    save(output/'doctor.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def verify(output):
    manifest = read(ROOT/'evidencia/manifiesto-copia.json')
    errors = []
    for row in manifest['files']:
        path = ROOT/'proyecto'/row['path']
        if not path.is_file():
            errors.append({'path':row['path'], 'error':'missing'})
            continue
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if digest != row['snapshot_sha256']:
            errors.append({'path':row['path'], 'error':'changed_since_delivery'})
    result = {'files':len(manifest['files']), 'errors':errors, 'status':'fail' if errors else 'pass'}
    save(output/'verify.json', result)
    print(json.dumps({'files':result['files'], 'errors':len(errors), 'status':result['status']}))
    if errors:
        raise RuntimeError('Transfer verification failed; changes after editing require a new manifest, not erasing this receipt')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action', choices=['doctor','verify','list','nuevo','plan','preview','check','preflight','render'])
    ap.add_argument('--video', type=int, default=31)
    ap.add_argument('--template', default='T01')
    ap.add_argument('--profile', choices=['pc-a-gtx1660ti','pc-b-uhd620','mac-auto'], default='mac-auto' if sys.platform=='darwin' else 'pc-a-gtx1660ti')
    ap.add_argument('--approve-render', action='store_true', help='Record explicit approval to render the reviewed candidate; does not replace editorial QA')
    args = ap.parse_args()
    if args.action == 'list':
        print(json.dumps(read(ROOT/'proyectos.json'), ensure_ascii=False, indent=2)); return
    if args.action == 'nuevo':
        new_project(args.video,args.template); return
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = ROOT/'resultados'/args.profile/f'VIDEO-{args.video:02d}'/stamp
    if args.action == 'verify':
        verify(output); return
    if args.action == 'doctor':
        doctor(output); return
    item, path = project(args.video)
    profile = read(ROOT/'perfiles'/f'{args.profile}.json')
    if args.action == 'plan':
        print(json.dumps({'project':str(path), 'hyperframes':item['hyperframes'], 'profile':profile,
                          'sfx_plan':item['sfx_plan_present'], 'hook_end':item['hook_end'],
                          'windows_validated':False}, ensure_ascii=False, indent=2)); return
    if not (path/'index.html').is_file():
        raise RuntimeError('New project is prepared but not composed: author editable/index.html using the selected template and new media first.')
    config = runtime()
    env = environment(config)
    command = cli(item, config)
    output.mkdir(parents=True)
    started = time.monotonic()
    status = 'fail'
    try:
        if args.action == 'preview':
            execute(command+['preview', str(path), '--background'], env=env)
            execute(command+['preview', str(path), '--status'], env=env)
        else:
            with machine_lock():
                if args.action in ('preflight', 'render'):
                    if args.action == 'render' and not args.approve_render:
                        raise RuntimeError('Review the candidate and supply --approve-render only after explicit approval')
                    preflight(item, path, config, output)
                if args.action in ('check', 'render'):
                    execute(command+['check', str(path)], env=env)
                if args.action == 'render':
                    help_text = execute(command+['render','--help'], capture=True, env=env)
                    flags = ['--workers', str(profile['render_workers'])]
                    if profile['low_memory'] and '--low-memory-mode' in help_text:
                        flags += ['--low-memory-mode']
                    elif profile['low_memory']:
                        print('Old CLI pin: low-memory flag unavailable; one worker only. Watch RAM.')
                    # Explicit delivery colour based on the selected existing export, not GPU type.
                    if item.get('delivery_transfer') == 'arib-std-b67':
                        if '--hdr' not in help_text:
                            raise RuntimeError('Pinned CLI lacks HDR export; resolve colour parity before rendering')
                        flags += ['--hdr']
                    execute(command+['render', str(path), '--output', str(output/'CANDIDATO.mp4')]+flags, env=env)
        status = 'pass'
    finally:
        save(output/'ejecucion.json', {'action':args.action, 'video':args.video, 'profile':args.profile,
             'status':status, 'seconds':round(time.monotonic()-started,3), 'hyperframes':item['hyperframes'],
             'platform':platform.platform(), 'render_requested_approval':args.approve_render,
             'final_mp4_qa':'pending', 'human_listening':'unconfirmed'})


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
