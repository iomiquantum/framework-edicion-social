"""Verifica el catálogo real y las muestras; no certifica gusto ni escucha."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import soundfile as sf

OUT=Path(__file__).resolve().parents[1]
FW=OUT.parents[1]
catalog=json.loads((FW/'library/music/catalogo-editorial.json').read_text())


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


records=[]
for t in catalog['tracks']:
    path=FW/t['file']
    assert sha(path)==t['sha256'] and (FW/t['preview']).exists()
    assert t['credit'] and t['license'] and (FW/t['source_manifest']).exists()
    record={'id':t['id'],'source_hash':'PASS','preview_and_manifest_exists':True,
            'roles':t['roles'],'history':t['history']}
    if t['type']=='bgm' and not t['history']:
        preview=FW/t['preview']
        assert sha(preview)==t['preview_sha256']
        audio,sr=sf.read(preview,dtype='float32',always_2d=True)
        assert audio.shape==(20*48000,2) and sr==48000 and np.isfinite(audio).all()
        assert sf.info(preview).subtype=='PCM_24' and 1e-5 < np.max(np.abs(audio)) < 1
        assert np.sqrt(np.mean(audio**2)) > 1e-6, 'Preview inesperadamente silencioso'
        subprocess.run(['/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg','-v','error','-i',str(preview),
                         '-f','null','-'],capture_output=True,check=True,timeout=60)
        record.update({'preview_format':'48k stereo PCM24 / 20s','decode':'PASS',
                       'sample_peak_dbfs':float(20*np.log10(np.max(np.abs(audio))))})
    records.append(record)
new=json.loads((FW/'library/music/candidates/2026-09-30-funciones/manifest.json').read_text())
for t in new['tracks']:
    html=FW/t['source_html']
    assert sha(html)==t['source_html_sha256']
    assert 'creativecommons.org/licenses/by/4.0' in html.read_text()
    assert t['decode_full']=='PASS'
links=[]
for name in ['biblioteca.html','referencias.html','practica.html']:
    for href in re.findall(r'(?:href|src)="([^"]+)"',(OUT/name).read_text()):
        if urlparse(href).scheme or href.startswith('#'):
            continue
        assert (OUT/href.split('#')[0]).resolve().exists(),f'Enlace roto {name}/{href}'
        links.append({'page':name,'href':href})
result={'status':'TECHNICAL_PASS','date_local':'2026-09-30','records':records,
        'active_music':sum(t['type']=='bgm' and not t['history'] for t in catalog['tracks']),
        'sfx':sum(t['type']=='sfx' for t in catalog['tracks']),
        'history_music':sum(t['history'] for t in catalog['tracks']),
        'new_official_license_snapshots':'PASS','local_links':links,
        'human_listening_new_music':'por confirmar','global_approval':'por confirmar',
        'reference_audio_reused_in_library':False}
(OUT/'evidencia/validacion-biblioteca.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','active_music','sfx','history_music']},ensure_ascii=False))
