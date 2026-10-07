#!/usr/bin/env python3
"""Medir comandos locales sin shell y conservar intentos y logs por separado.

Estos eventos son evidencia parcial; no sustituyen production-metrics.json,
QA, aprobación, tiempo total de edición ni contadores de tokens/costo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone
from uuid import uuid4


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def file_record(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return {'path': str(path.resolve()), 'bytes': path.stat().st_size,
            'sha256': digest.hexdigest()}


def measure(*, out, scope, phase, command, cwd=None, reason=None):
    if not command:
        raise ValueError('Falta un comando después de --')
    working_dir = Path(cwd or Path.cwd()).resolve(strict=True)
    if not working_dir.is_dir():
        raise ValueError('cwd debe ser una carpeta')
    event_dir = Path(out).resolve() / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid4().hex)
    event_dir.mkdir(parents=True, exist_ok=False)
    started_at, start = utc_now(), time.monotonic()
    launch_error = None
    with (event_dir / 'stdout.log').open('wb') as stdout, (event_dir / 'stderr.log').open('wb') as stderr:
        try:
            result = subprocess.run(command, cwd=working_dir, stdout=stdout, stderr=stderr, shell=False)
            exit_code = result.returncode
        except OSError as error:
            exit_code, launch_error = 127, str(error)
            stderr.write((launch_error + '\n').encode())
    wall_s, ended_at = time.monotonic() - start, utc_now()
    event = {
        'event_version': 1, 'event_id': event_dir.name, 'scope': scope,
        'phase': phase, 'command': command, 'cwd': str(working_dir),
        'started_at': started_at, 'ended_at': ended_at, 'wall_s': wall_s,
        'measurement_method': 'monotonic_subprocess_wall',
        'exit_code': exit_code, 'status': 'pass' if exit_code == 0 else 'fail',
        'reason': reason, 'launch_error': launch_error,
        'logs': [file_record(event_dir / name) for name in ('stdout.log', 'stderr.log')],
        'limits': 'Solo tiempo del comando y sus hijos esperados. No incluye decisiones, espera humana ni procesos desacoplados; no afirma QA/aprobación. Entorno no registrado: configuración/versiones deben ligarse mediante los logs/manifiestos del comando.'
    }
    (event_dir / 'event.json').write_text(json.dumps(event, ensure_ascii=False, indent=2) + '\n')
    return event_dir, event


def interval_union_seconds(intervals):
    merged = []
    for start, end in sorted(intervals):
        if end < start:
            raise ValueError('Intervalo UTC invertido; comprobar reloj')
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return sum((end - start).total_seconds() for start, end in merged)


def summarize(root, scope=None):
    events = [json.loads(path.read_text()) for path in sorted(Path(root).glob('*/event.json'))]
    events = [event for event in events if scope is None or event['scope'] == scope]
    phases = {}
    intervals = []
    for event in events:
        for log in event['logs']:
            actual = file_record(Path(log['path']))
            if actual != log:
                raise ValueError('Log alterado: ' + log['path'])
        row = phases.setdefault(event['phase'], {'attempts': 0, 'failed': 0, 'sum_process_wall_s': 0.0})
        row['attempts'] += 1
        row['failed'] += event['exit_code'] != 0
        row['sum_process_wall_s'] += event['wall_s']
        intervals.append((datetime.fromisoformat(event['started_at']), datetime.fromisoformat(event['ended_at'])))
    return {'scope_filter': scope, 'events': len(events), 'phases': phases,
            'sum_process_wall_s': sum(event['wall_s'] for event in events),
            'union_observed_command_intervals_s': interval_union_seconds(intervals),
            'limits': 'Suma de comandos puede solaparse y no es tiempo total de edición. Unión usa reloj UTC local y excluye huecos/espera/decisiones. No comparar lotes con cobertura de medición distinta; logs locales no autentican aprobación ni evidencia humana.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    run = sub.add_parser('run')
    run.add_argument('--out', type=Path, required=True)
    run.add_argument('--scope', required=True, help='VIDEO-16 o LOTE-16-20; no duplicar ingesta en cada video')
    run.add_argument('--phase', required=True)
    run.add_argument('--cwd', type=Path)
    run.add_argument('--reason', help='Motivo del intento o causa de retrabajo')
    run.add_argument('command', nargs=argparse.REMAINDER)
    report = sub.add_parser('summary')
    report.add_argument('--events', type=Path, required=True)
    report.add_argument('--scope')
    args = parser.parse_args(argv)
    try:
        if args.action == 'summary':
            print(json.dumps(summarize(args.events, args.scope), ensure_ascii=False, indent=2))
            return 0
        command = args.command[1:] if args.command[:1] == ['--'] else args.command
        event_dir, event = measure(out=args.out, scope=args.scope, phase=args.phase, command=command, cwd=args.cwd, reason=args.reason)
        print(json.dumps({'event': str(event_dir / 'event.json'), 'status': event['status'], 'exit_code': event['exit_code'], 'wall_s': round(event['wall_s'], 3)}))
        return event['exit_code'] if event['exit_code'] >= 0 else 128 - event['exit_code']
    except (OSError, ValueError, KeyError) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
