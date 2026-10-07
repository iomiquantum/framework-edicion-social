"""Validate documentation integration and unchanged sampled media; no rendering."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FW = ROOT / 'Framework-Edicion-Social'
HERE = Path(__file__).resolve().parent


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024),b''):
            h.update(b)
    return h.hexdigest()


checks = []
json_paths = [FW/'captions/catalog.json', FW/'templates/caption-decision.json',
              FW/'rules/registry.json', FW/'sources/catalog.json',
              HERE/'source-notes.json', HERE/'export-audit.json', HERE/'export-audit.before-visual-review.json']
data = {str(p):json.loads(p.read_text()) for p in json_paths}
checks.append(dict(id='JSON_PARSE',status='pass',count=len(json_paths)))
catalog = data[str(FW/'captions/catalog.json')]
template = data[str(FW/'templates/caption-decision.json')]
formats = {f['id'] for f in catalog['formats']}
assert len(formats)==4 and len(catalog['placements'])==3
assert template['main_format_id'] is None and template['status']=='template_not_a_completed_review'
assert catalog['performance_status']=='por_confirmar' and not catalog['automatic_selector_implemented']
assert not catalog['defaults']['numeric_thresholds_are_automatic_fail']
for f in catalog['formats']:
    assert not f.get('fallback') or f['fallback'] in formats
checks.append(dict(id='CATALOG_TEMPLATE_CONTRACT',status='pass',formats=sorted(formats),placements=3))

schema = json.loads((FW/'schemas/rule.schema.json').read_text())
registry = data[str(FW/'rules/registry.json')]
old_registry = json.loads((HERE/'before-framework-update/Framework-Edicion-Social/rules/registry.json').read_text())
new_ids = {'CAPTION_CONTEXTUAL_FORMAT_SELECTION','CAPTION_MOBILE_READABILITY_AND_STABLE_LAYOUT','CAPTION_DESTINATION_UI_EVIDENCE'}
new_rules = [r for r in registry['rules'] if r['id'] in new_ids]
assert len(new_rules)==3
for r in new_rules:
    assert set(schema['required']) <= set(r)
    for key in ['kind','status','confidence']:
        assert r[key] in schema['properties'][key]['enum']
    assert re.fullmatch(r'[A-Z0-9_]+',r['id'])
    assert re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',r['version'])
    datetime.strptime(r['review_due_at'],'%Y-%m-%d')
    assert isinstance(r['scope'],dict) and isinstance(r['instruction'],str) and r['instruction']
assert [r for r in registry['rules'] if r['id'] not in new_ids] == old_registry['rules']
assert len({r['id'] for r in registry['rules']})==len(registry['rules'])
checks.append(dict(id='NEW_RULES_FIELDS_ENUMS_AND_OLD_RULES_PRESERVED',status='pass',new_rules=3,
                   method='Required fields/enums from schema plus ID/version/date checks; not a general JSON Schema engine.'))

sources = data[str(FW/'sources/catalog.json')]
old_sources = json.loads((HERE/'before-framework-update/Framework-Edicion-Social/sources/catalog.json').read_text())
assert sources['sources'][:len(old_sources['sources'])] == old_sources['sources']
assert sources['verified_at'] == old_sources['verified_at']
source_ids = {s['id'] for s in sources['sources']}
assert len(source_ids)==len(sources['sources'])
assert all(set(r['evidence'])<=source_ids for r in new_rules)
checks.append(dict(id='SOURCE_LINKAGE_AND_OLD_VERIFICATION_DATE_PRESERVED',status='pass',new_sources=10))

docs = [FW/'README.md',FW/'PROMPT_EDICION_INDIVIDUAL.md',FW/'QA_PROFESIONAL.md',
        FW/'PROMPT_INGESTA_Y_EDICION.md',FW/'PROMPT_DERIVADOS_PLATAFORMA.md',
        ROOT/'Serie-IA-Negocios-10-Videos/AGENTS.md']
for p in docs:
    assert 'SUBTITULOS_CONTEXTO_Y_LECTURA.md' in p.read_text()
checks.append(dict(id='WORKFLOW_REFERENCES',status='pass',documents=len(docs)))

mds = [FW/'SUBTITULOS_CONTEXTO_Y_LECTURA.md',HERE/'INFORME.md']
local_links=[]
for p in mds:
    for raw in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if raw.startswith(('https://','http://','#')):
            continue
        dest=(p.parent/raw.split('#')[0]).resolve()
        assert dest.exists(), f'Missing markdown target: {p}: {raw}'
        local_links.append(str(dest))
checks.append(dict(id='LOCAL_MARKDOWN_LINKS',status='pass',count=len(local_links)))

audit = data[str(HERE/'export-audit.json')]
assert audit['status']=='scoped_visual_review_complete'
assert audit['totals']==dict(exports=18, selected_frames=54,editable_cues=189,
                           editable_cues_above20cps=31,threshold_provenance='internal_review_reference_not_automatic_failure')
media=[]
for v in audit['videos']:
    assert sha(v['file'])==v['sha256']
    assert v['visual_review_completed'] and v['visual_review_scope']=='three selected frames only'
    for f in v['review_frames']:
        assert sha(f['path'])==f['sha256']
    media.append(dict(video_id=v['video_id'],path=v['file'],sha256=v['sha256'],unchanged=True))
checks.append(dict(id='EXPORT_AND_SAMPLE_INTEGRITY',status='pass',exports=18,frames=54))
approval=json.loads((ROOT/'Serie-IA-Negocios-10-Videos/VIDEO-16/APROBACION_VIDEO_16_V4.json').read_text())
v16=next(v for v in audit['videos'] if v['video_id']=='VIDEO-16')
assert approval['approved'] and approval['output']['sha256']==v16['sha256']
checks.append(dict(id='V16_EXISTING_APPROVAL_BINDING',status='pass',prior_approval_preserved=True))

manifest = dict(checked_at_utc=datetime.now(timezone.utc).isoformat(),status='pass',checks=checks,
                unchanged_media=media,scope='Documentation/catalog/link/schema/hash verification, not full video QA or live UI.',
                visual_comparison_review='Six-sample contact sheet visually inspected by Codex root after generation.',
                physical_phone_test=False,full_muted_playback_in_this_audit=False,live_platform_preview=False,
                files=[dict(path=str(p),sha256=sha(p)) for p in json_paths+docs+mds+[HERE/'COMPARACION_6_EXPORTACIONES.png']])
(HERE/'validation.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(status='pass',checks=len(checks),exports_unchanged=18,selected_frames=54,
                      report=str(HERE/'validation.json')),ensure_ascii=False))
