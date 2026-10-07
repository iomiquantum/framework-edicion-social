#!/usr/bin/env python3
"""Registrar intervalos de edición entre procesos, sin ejecutar tareas ni aprobar QA.

start/stop usan time.time y UTC: el reloj del sistema puede ajustarse; esto no es
una medición monotónica entre invocaciones. Solo se contabilizan intervalos
cerrados. El journal inmutable es la fuente de verdad y state.json es su caché.
No modifica run.json, perfiles, medios, verificaciones ni aprobaciones.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import portable_fcntl as fcntl
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time
from uuid import UUID, uuid4


PHASES = (
    'intake', 'semantic_lock', 'resources', 'assembly', 'review_changes',
    'qa_pre_render', 'render', 'qa_post_render', 'documentation', 'coordination',
)
KINDS = ('work', 'command', 'user_wait', 'experiment_audit')
METHOD = 'utc_wall_clock_time_time_cross_process'


def _epoch(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('El reloj debe devolver segundos epoch finitos')
    return float(value)


def _utc(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat()


def interval_union_seconds(intervals):
    """Unión de intervalos epoch; los solapamientos no se suman dos veces."""
    merged = []
    for start, end in sorted((_epoch(start), _epoch(end)) for start, end in intervals):
        if end < start:
            raise ValueError('Intervalo invertido; comprobar el reloj del sistema')
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return sum(end - start for start, end in merged)


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def _sync_directory(path):
    descriptor = os.open(path, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_json(path, value, *, replace):
    """Publicar un JSON completo; los eventos nunca reemplazan archivos existentes."""
    descriptor, temporary = tempfile.mkstemp(prefix='.pending-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as handle:
            handle.write(_json_bytes(value))
            handle.flush()
            os.fsync(handle.fileno())
        if replace:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)  # Publicación atómica y exclusiva, sin sobrescritura.
        _sync_directory(path.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def _locked_timing(run):
    timing = Path(run).resolve() / 'timing'
    (timing / 'events').mkdir(parents=True, exist_ok=True)
    with (timing / '.lock').open('a+b') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            yield timing
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def _read_journal(timing):
    events = []
    for path in (timing / 'events').glob('*.json'):
        event = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(event, dict) or event.get('schema_version') != 1:
            raise ValueError('Evento incompatible: ' + str(path))
        identifier = event.get('event_id')
        if not isinstance(identifier, str) or str(UUID(identifier)) != identifier or path.stem != identifier:
            raise ValueError('UUID o nombre de evento inválido: ' + str(path))
        if type(event.get('sequence')) is not int or event['sequence'] < 1:
            raise ValueError('Secuencia de evento inválida: ' + str(path))
        if event.get('phase') not in PHASES or event.get('kind') not in KINDS:
            raise ValueError('Fase o tipo desconocido en evento: ' + str(path))
        events.append(event)
    events.sort(key=lambda event: event['sequence'])
    opened, intervals, previous_epoch = None, [], None
    for expected, event in enumerate(events, 1):
        if event['sequence'] != expected:
            raise ValueError('Journal con secuencias duplicadas o faltantes; conservar y revisar los eventos')
        stamp = _epoch(event['at_epoch_seconds'])
        if event.get('at_utc') != _utc(stamp):
            raise ValueError('UTC y epoch no coinciden en evento ' + event['event_id'])
        if previous_epoch is not None and stamp < previous_epoch:
            raise ValueError('Reloj invertido en el journal; no se pueden certificar duraciones')
        previous_epoch = stamp
        if event.get('action') == 'start':
            if opened is not None or event.get('interval_id') != event['event_id']:
                raise ValueError('Journal con inicios superpuestos o identidad inválida')
            opened = event
        elif event.get('action') == 'stop':
            if opened is None or any(event.get(key) != opened[key] for key in ('interval_id', 'phase', 'kind')):
                raise ValueError('Cierre sin inicio coincidente en el journal')
            intervals.append({
                'interval_id': opened['interval_id'], 'phase': opened['phase'], 'kind': opened['kind'],
                'started_at_utc': opened['at_utc'], 'ended_at_utc': event['at_utc'],
                'started_epoch_seconds': opened['at_epoch_seconds'], 'ended_epoch_seconds': stamp,
                'seconds': stamp - opened['at_epoch_seconds'],
                'start_note': opened.get('note'), 'stop_note': event.get('note'),
            })
            opened = None
        else:
            raise ValueError('Acción desconocida en evento ' + event['event_id'])
    return events, opened, intervals


def _record(run, *, action, phase=None, kind='work', note=None, clock=time.time):
    if action == 'start' and (phase not in PHASES or kind not in KINDS):
        raise ValueError('Fase o tipo desconocido; consultar --help')
    if note is not None and not isinstance(note, str):
        raise ValueError('La nota debe ser texto')
    with _locked_timing(run) as timing:
        events, opened, _ = _read_journal(timing)
        if action == 'start' and opened is not None:
            raise ValueError('Ya existe un intervalo abierto: ' + opened['phase'])
        if action == 'stop' and opened is None:
            raise ValueError('No existe un intervalo abierto que cerrar')
        stamp = _epoch(clock())
        if events and stamp < events[-1]['at_epoch_seconds']:
            raise ValueError('El reloj retrocedió; no se guardó el evento. Comprobar el reloj del sistema')
        identifier = str(uuid4())
        event = {
            'schema_version': 1, 'event_id': identifier, 'sequence': len(events) + 1,
            'action': action, 'interval_id': identifier if action == 'start' else opened['interval_id'],
            'phase': phase if action == 'start' else opened['phase'],
            'kind': kind if action == 'start' else opened['kind'],
            'at_epoch_seconds': stamp, 'at_utc': _utc(stamp), 'note': note,
            'measurement_method': METHOD,
        }
        _atomic_json(timing / 'events' / (identifier + '.json'), event, replace=False)
        _atomic_json(timing / 'state.json', {
            'schema_version': 1, 'last_event_sequence': event['sequence'],
            'last_event_id': identifier, 'open_interval': event if action == 'start' else None,
            'state_is_cache': True,
        }, replace=True)
        return event


def start_interval(run, phase, *, kind='work', note=None, clock=time.time):
    return _record(run, action='start', phase=phase, kind=kind, note=note, clock=clock)


def stop_interval(run, *, note=None, clock=time.time):
    return _record(run, action='stop', note=note, clock=clock)


def _total(rows):
    return {
        'status': 'measured' if rows else 'not_measured', 'intervals': len(rows),
        'total_seconds': sum(row['seconds'] for row in rows) if rows else None,
    }


def summarize(run):
    with _locked_timing(run) as timing:
        events, opened, intervals = _read_journal(timing)
    pairs = [(row['started_epoch_seconds'], row['ended_epoch_seconds']) for row in intervals]
    span = intervals[-1]['ended_epoch_seconds'] - events[0]['at_epoch_seconds'] if intervals else None
    observed = interval_union_seconds(pairs) if intervals else None
    operational = [(row['started_epoch_seconds'], row['ended_epoch_seconds'])
                   for row in intervals if row['kind'] in ('work', 'command')]
    waits = [row for row in intervals if row['kind'] == 'user_wait']
    audits = [row for row in intervals if row['kind'] == 'experiment_audit']
    phases = {}
    for phase in PHASES:
        rows = [row for row in intervals if row['phase'] == phase]
        phases[phase] = _total(rows)
        phases[phase]['kinds'] = {kind: _total([row for row in rows if row['kind'] == kind]) for kind in KINDS}
    return {
        'schema_version': 1, 'run': str(Path(run).resolve()), 'measurement_method': METHOD,
        'status': 'in_progress' if opened else ('measured' if intervals else 'not_measured'),
        'events': len(events), 'closed_intervals': len(intervals),
        'open_interval': opened, 'intervals': intervals, 'phases': phases,
        'kinds': {kind: _total([row for row in intervals if row['kind'] == kind]) for kind in KINDS},
        'span_started_at_utc': events[0]['at_utc'] if intervals else None,
        'span_ended_at_utc': intervals[-1]['ended_at_utc'] if intervals else None,
        'elapsed_span_seconds': span, 'observed_union_seconds': observed,
        'unmeasured_gaps_seconds': max(0.0, span - observed) if intervals else None,
        'observed_operational_union_seconds': interval_union_seconds(operational) if operational else None,
        'observed_user_wait_seconds': _total(waits)['total_seconds'],
        'observed_experiment_audit_seconds': _total(audits)['total_seconds'],
        'limits': (
            'Solo intervalos cerrados del journal; el abierto queda excluido. El span termina en el último stop: '
            'no incluye espera posterior ni tiempo previo al primer start. Los huecos no identifican su causa. '
            'work y command son etiquetas de tiempo transcurrido, no actividad humana continua; user_wait y '
            'experiment_audit se informan por separado. La unión operativa incluye solo work/command medidos, '
            'sin asignar huecos ni espera/auditoría al trabajo. No suma ni importa tiempos de subprocessos. '
            'UTC/time.time usa reloj de pared, no monotónico entre procesos. No afirma tokens, costo, ahorro, '
            'QA, escucha ni aprobación; no comparar ejecuciones con cobertura distinta.'
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    start = sub.add_parser('start', help='Abrir un intervalo; no puede existir otro abierto')
    start.add_argument('--run', type=Path, required=True)
    start.add_argument('--phase', choices=PHASES, required=True)
    start.add_argument('--kind', choices=KINDS, default='work')
    start.add_argument('--note')
    stop = sub.add_parser('stop', help='Cerrar el intervalo actual')
    stop.add_argument('--run', type=Path, required=True)
    stop.add_argument('--note')
    report = sub.add_parser('summary', help='Informar intervalos cerrados, huecos y estado abierto')
    report.add_argument('--run', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == 'start':
            result = start_interval(args.run, args.phase, kind=args.kind, note=args.note)
        elif args.action == 'stop':
            result = stop_interval(args.run, note=args.note)
        else:
            result = summarize(args.run)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
