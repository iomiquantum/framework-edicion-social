"""Local, atomic student progress. Fixed file names; no browser-selected write paths."""
from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path
import re
import tempfile
import threading
import time
import uuid
import portable_fcntl

ROOT = Path(__file__).resolve().parents[1]
LOCK = threading.RLock()
STEP_COUNTS = dict(welcome=2, folder=2, launcher=2, diagnosis=2, manager=1,
                   install=3, verify=3, context=2, palette=2, templates=2,
                   recording=2, masters=2, batch=2, codex=2, return_=2)
STEP_COUNTS['return'] = STEP_COUNTS.pop('return_')
FILES = {'guia': 'guia.json', 'borrador': 'borrador-edicion.json', 'ultimo-lote': 'ultimo-lote.json', 'grabacion': 'guion-grabacion.json'}
FIELDS = ('title topic audience goal tone platform cta avoid script motion brand language '
          'attachments masters count duration profile style_preference').split()


class Conflict(ValueError):
    pass


def now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


@contextlib.contextmanager
def locked():
    folder = ROOT / 'MI-PROGRESO'
    folder.mkdir(parents=True, exist_ok=True)
    # A separate lock lets notes save while an installation/render holds the heavy-job lock.
    with LOCK, (folder / '.guardado.lock').open('a+b') as handle:
        if handle.tell() == 0:
            handle.write(b'\0'); handle.flush()
        portable_fcntl.flock(handle, portable_fcntl.LOCK_EX)
        try:
            yield folder
        finally:
            portable_fcntl.flock(handle, portable_fcntl.LOCK_UN)


def atomic(path, data):
    raw = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8') + b'\n'
    fd, name = tempfile.mkstemp(prefix='.' + path.name, suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)


def validate(kind, data):
    if not isinstance(data, dict): raise ValueError('Los datos de progreso no son válidos.')
    if len(json.dumps(data).encode()) > 450000: raise ValueError('Demasiado texto para guardar; adjunta el guion como archivo.')
    if kind == 'guia':
        if data.get('schema') != 'framework.guia.progreso' or data.get('version') != 1 or data.get('activeOS') not in ('', 'windows', 'mac'):
            raise ValueError('Versión de progreso no compatible.')
        clean = {k: data[k] for k in ('schema', 'version', 'activeOS')}; clean['paths'] = {}
        for system in ('windows', 'mac'):
            path = data.get('paths', {}).get(system)
            if not isinstance(path, dict) or path.get('step') not in STEP_COUNTS:
                raise ValueError('Paso de la guía inválido.')
            item = {'step': path['step'], 'checks': {}, 'notes': {}, 'updatedAt': None}
            if isinstance(path.get('updatedAt'), str): item['updatedAt'] = path['updatedAt'][:40]
            for key, count in STEP_COUNTS.items():
                values = path.get('checks', {}).get(key)
                if values is not None:
                    if not isinstance(values, list) or len(values) != count or any(type(v) is not bool for v in values):
                        raise ValueError('Casillas inválidas.')
                    item['checks'][key] = values
                note = path.get('notes', {}).get(key)
                if note is not None:
                    if not isinstance(note, str) or len(note) > 3000: raise ValueError('Nota demasiado larga o inválida.')
                    item['notes'][key] = note
            clean['paths'][system] = item
        return clean
    if kind == 'borrador':
        clean = {}
        for name in FIELDS:
            value = data.get(name, '')
            if not isinstance(value, str) or len(value) > 20000: raise ValueError('Campo demasiado largo: ' + name)
            clean[name] = value
        templates = data.get('templates', [])
        if not isinstance(templates, list) or len(templates) > 30 or any(not isinstance(t, str) or not re.fullmatch(r'T(?:0[1-9]|[12][0-9]|30)', t) for t in templates):
            raise ValueError('Selección de plantillas inválida.')
        colors = data.get('colors')
        if colors is not None and (not isinstance(colors, list) or len(colors) != 4 or any(not isinstance(c, str) or not re.fullmatch(r'#[a-fA-F0-9]{6}', c) for c in colors)):
            raise ValueError('Paleta inválida.')
        palette = data.get('palette', 'bosque')
        if not isinstance(palette, str) or not re.fullmatch(r'[a-z0-9_-]{1,60}', palette): raise ValueError('Identificador de paleta inválido.')
        step = data.get('step', 0)
        if type(step) is not int or not 0 <= step <= 5: raise ValueError('Paso del asistente inválido.')
        clean.update(templates=list(dict.fromkeys(templates)), colors=colors, palette=palette, step=step)
        return clean
    if kind == 'grabacion':
        clean = {}
        for key in ('hook', 'body', 'close', 'notes'):
            value = data.get(key, '')
            if not isinstance(value, str) or len(value) > 10000: raise ValueError('Texto de grabación inválido.')
            clean[key] = value
        for key in ('video', 'take'):
            value = data.get(key, 31 if key == 'video' else 1)
            if type(value) is not int or not 1 <= value <= 9998: raise ValueError('Número de video/toma inválido.')
            clean[key] = value
        case = data.get('case', 'correct')
        if case not in ('correct', 'correction', 'discard', 'batch'): raise ValueError('Ejemplo inválido.')
        checks = data.get('checks', [False] * 6)
        if not isinstance(checks, list) or len(checks) != 6 or any(type(x) is not bool for x in checks): raise ValueError('Checklist inválido.')
        clean.update(case=case, checks=checks)
        return clean
    if kind == 'ultimo-lote':
        if not isinstance(data.get('folder'), str) or not isinstance(data.get('prompt'), str): raise ValueError('Recibo de lote inválido.')
        return data
    raise ValueError('Tipo de progreso desconocido.')


def _read(folder, kind):
    if kind not in FILES: raise ValueError('Archivo de progreso desconocido.')
    path = folder / FILES[kind]
    if not path.exists(): return {'revision': 0, 'updated_at': None, 'data': None}
    for candidate in (path, path.with_suffix('.anterior.json')):
        try:
            result = json.loads(candidate.read_text(encoding='utf-8'))
            if type(result['revision']) is not int or result['revision'] < 1: raise ValueError('Revisión inválida')
            result['data'] = validate(kind, result['data'])
            if candidate != path: result['warning'] = 'Se recuperó la copia anterior del progreso porque la última no pudo leerse.'
            return result
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            continue
    raise ValueError('No se pudo leer el progreso ni su copia anterior. Conserva MI-PROGRESO y pide ayuda; no se sobrescribirá.')


def read(kind):
    with locked() as folder: return _read(folder, kind)


def write(kind, data, revision=None):
    clean = validate(kind, data)
    with locked() as folder:
        old = _read(folder, kind)
        if revision is not None and (type(revision) is not int or revision != old['revision']):
            raise Conflict('El progreso cambió en otra ventana. Descarga una copia de tus notas y recarga para recuperar lo más reciente.')
        result = {'revision': old['revision'] + 1, 'updated_at': now(), 'data': clean}
        path = folder / FILES[kind]
        if old['data'] is not None: atomic(path.with_suffix('.anterior.json'), {k: v for k, v in old.items() if k != 'warning'})
        atomic(path, result)
        return {'revision': result['revision'], 'updated_at': result['updated_at'], 'saved': True}


def event(name, status, detail=''):
    with locked() as folder:
        row = {'at': now(), 'action': name[:60], 'status': status[:30], 'detail': str(detail)[:2000]}
        with (folder / 'acciones.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + '\n'); handle.flush()


def backup(kind, data):
    clean = validate(kind, data)
    with locked() as folder:
        destination=folder/'copias';destination.mkdir(exist_ok=True)
        path=destination/('PROGRESO-'+kind.upper()+'-'+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]+'.json')
        atomic(path,clean)
        return {'saved':True,'path':str(path),'relative_path':path.relative_to(ROOT).as_posix()}


def copies(name=None):
    with locked() as folder:
        folder=folder/'copias'
        if name is not None:
            if not re.fullmatch(r'PROGRESO-GUIA-\d{8}-\d{6}-[a-f0-9]{6}\.json',name):raise ValueError('Copia desconocida.')
            return validate('guia',json.loads((folder/name).read_text(encoding='utf-8')))
        return sorted([f.name for f in folder.glob('PROGRESO-GUIA-*.json') if re.fullmatch(r'PROGRESO-GUIA-\d{8}-\d{6}-[a-f0-9]{6}\.json',f.name)],reverse=True)
