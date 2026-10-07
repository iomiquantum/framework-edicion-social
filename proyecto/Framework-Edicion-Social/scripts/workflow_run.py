#!/usr/bin/env python3
"""Select an additive editing profile and index trial evidence; never render or approve."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
KINDS = ('full_check', 'targeted_check', 'correction', 'full_render', 'failed_render',
         'image_generated', 'image_unused', 'escalation', 'candidate_ready', 'local_delivery_completed')

def now(): return datetime.now(timezone.utc).isoformat()
def record(path):
    p = Path(path).resolve(strict=True)
    if not p.is_file(): raise ValueError('Evidence must be a file: ' + str(p))
    return {'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'size_bytes': p.stat().st_size}

def write_new(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')

def profile(flow):
    p = ROOT / 'workflow-profiles' / f'flujo-{flow}.json'
    d = json.loads(p.read_text())
    if d['profile_id'] != f'flujo-{flow}' or not d['safety_floor_required']:
        raise ValueError('Invalid editing profile')
    return p, d

def init(out, video, flow=1, trial=None):
    if not re.fullmatch(r'VIDEO-\d{2,}', video): raise ValueError('Invalid VIDEO-NN')
    path, selected = profile(flow)
    run = Path(out).resolve()
    if run.exists(): raise ValueError('Run already exists; keep previous runs')
    run.mkdir(parents=True)
    frozen=run/'frozen';frozen.mkdir()
    floor=ROOT/'workflow-profiles/QA_COMUN.md'
    (frozen/'profile.json').write_bytes(path.read_bytes())
    (frozen/'QA_COMUN.md').write_bytes(floor.read_bytes())
    data = {'schema_version':'1.0.0', 'run_id':str(uuid4()), 'video_id':video,
            'trial_id':trial, 'created_at':now(), 'profile':selected,
            'profile_source':record(path),
            'safety_floor':record(floor),
            'profile_frozen':record(frozen/'profile.json'),
            'safety_floor_frozen':record(frozen/'QA_COMUN.md'),
            'status':'prepared_not_started', 'approval_status':'not_inferred',
            'limits':'Profile selection is not QA, approval, publication or restoration authorization.'}
    write_new(run/'run.json',data)
    (run/'events').mkdir()
    return data

def read_run(run):
    run = Path(run).resolve(strict=True)
    d = json.loads((run/'run.json').read_text())
    for name in ('profile_frozen','safety_floor_frozen'):
        if record(d[name]['path']) != d[name]:
            raise ValueError('Frozen profile/rules changed; preserve historical run integrity')
    d['live_rules_changed']=any(record(d[name]['path'])!=d[name] for name in ('profile_source','safety_floor'))
    return run,d

def event(run, kind, note, evidence=None):
    run,d = read_run(run)
    if d['live_rules_changed']:
        raise ValueError('Live profile/rules changed; open a new versioned run before new work events')
    if kind not in KINDS: raise ValueError('Unknown event kind')
    if kind in ('candidate_ready','local_delivery_completed') and evidence is None:
        raise ValueError('Milestone needs concrete candidate/delivery evidence; not inferred')
    e = {'event_id':str(uuid4()), 'run_id':d['run_id'], 'at':now(), 'kind':kind,
         'note':note, 'evidence':record(evidence) if evidence else None,
         'measurement_method':'explicit_logged_event_not_automatic_detection'}
    write_new(run/'events'/f"{e['event_id']}.json",e)
    return e

def report(run, evidence=()):
    run,d = read_run(run)
    events = [json.loads(p.read_text()) for p in sorted((run/'events').glob('*.json'))]
    for e in events:
        if e['run_id']!=d['run_id']: raise ValueError('Mixed run events')
        if e['evidence'] and record(e['evidence']['path'])!=e['evidence']:
            raise ValueError('Event evidence changed; preserve previous file')
    timer_path=ROOT/'scripts/medir_fases_edicion.py'
    spec=importlib.util.spec_from_file_location('workflow_phase_timer',timer_path)
    timer=importlib.util.module_from_spec(spec);spec.loader.exec_module(timer)
    return {'schema_version':'1.0.0','generated_at':now(),'run_id':d['run_id'],
            'video_id':d['video_id'],'profile_id':d['profile']['profile_id'],
            'profile_version':d['profile']['version'],'profile_status':d['profile']['status'],
            'live_rules_changed':d['live_rules_changed'],
            'timing':timer.summarize(run),
            'event_counts':{kind:sum(e['kind']==kind for e in events) for kind in KINDS},
            'milestones':{kind: min((e['at'] for e in events if e['kind']==kind), default=None)
                          for kind in ('candidate_ready','local_delivery_completed')},
            'events':events,'evidence_index':[record(p) for p in evidence],
            'qa_status':'not_evaluated_by_this_report','approval_status':'not_evaluated_by_this_report',
            'limits':'Counts cover explicit logs only; an absent event does not prove no rework. Timers do not establish quality, listening, causal savings, tokens or cost. This report does not write bitacora/changelogs.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('init');p.add_argument('--out',type=Path,required=True);p.add_argument('--video',required=True);p.add_argument('--flow',type=int,choices=(1,2,3),default=1);p.add_argument('--trial')
    p=sub.add_parser('event');p.add_argument('--run',type=Path,required=True);p.add_argument('--kind',choices=KINDS,required=True);p.add_argument('--note',required=True);p.add_argument('--evidence',type=Path)
    p=sub.add_parser('report');p.add_argument('--run',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--evidence',type=Path,action='append',default=[])
    args=parser.parse_args()
    try:
        if args.action=='init':result=init(args.out,args.video,args.flow,args.trial)
        elif args.action=='event':result=event(args.run,args.kind,args.note,args.evidence)
        else:
            result=report(args.run,args.evidence);write_new(args.out,result)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,KeyError) as error:
        print('ERROR: '+str(error),file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
