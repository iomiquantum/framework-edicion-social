"""Comprueba las mezclas reales de investigación, sin certificar escucha."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1]
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
EVID = OUT / 'evidencia/practica-v1'
DATA = json.loads((EVID/'manifest.json').read_text())
N = round(DATA['duration_s']*48000)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def decode(p):
    proc = subprocess.run([FF, '-v', 'error', '-i', str(p), '-vn', '-ar', '48000',
                           '-ac', '2', '-f', 'f32le', '-'], capture_output=True, timeout=60)
    assert proc.returncode == 0, proc.stderr.decode()
    return np.frombuffer(proc.stdout, '<f4').reshape(-1,2)[:N].copy()


def corr(a,b):
    return float(np.corrcoef(a.reshape(-1), b.reshape(-1))[0,1])


assert sha(ROOT/DATA['picture_source']) == DATA['picture_source_sha256']
assert sha(ROOT/DATA['voice_source']) == DATA['voice_source_sha256']
for e in DATA['sfx_events']:
    assert sha(ROOT/e['source']) == e['source_sha256']
pcms, aacs, exports = {}, {}, []
for v in DATA['variants']:
    wav, mp4 = OUT/v['wav'], OUT/v['mp4']
    assert sha(wav) == v['wav_sha256'] and sha(mp4) == v['mp4_sha256']
    pcms[v['id']], aacs[v['id']] = decode(wav), decode(mp4)
    agreement = corr(pcms[v['id']], aacs[v['id']])
    assert agreement > .995, 'El MP4 no corresponde al PCM esperado'
    exports.append({'id':v['id'], 'hashes':'pass', 'aac_pcm_correlation':agreement})
effects = decode(OUT/'audiciones/practica-v1/efectos-solos.wav')
music = decode(OUT/'audiciones/practica-v1/cama-aplicada.wav')
a,b,c = '00-referencia-voz','01-voz-efectos','02-voz-efectos-pulso'
error_sfx = float(np.max(np.abs((pcms[b]-pcms[a])-effects)))
error_music = float(np.max(np.abs((pcms[c]-pcms[b])-music)))
assert error_sfx < 4e-7 and error_music < 4e-7, 'Voz/mezcla cambió más allá de cuantización PCM24'
events=[]
for e in DATA['sfx_events']:
    i,j=round(e['start']*48000),round((e['start']+e['duration_s'])*48000)
    agreement=corr((aacs[b]-aacs[a])[i:j],effects[i:j])
    assert agreement>.90, 'SFX no identificado en la diferencia de MP4'
    events.append({'id':e['id'],'aac_difference_sfx_correlation':agreement,
                   'human_audibility':'por confirmar'})
i,j=round(2.09*48000),round(13.39*48000)
music_agreement=corr((aacs[c]-aacs[b])[i:j],music[i:j])
assert music_agreement>.90
# Enlaces HTML locales y rutas de las tres elecciones; no valida webs externas.
links=[]
for name in ['practica.html','voz.html']:
    html=(OUT/name).read_text()
    for href in re.findall(r'(?:href|src)="([^"]+)"',html):
        if urlparse(href).scheme or href.startswith('#'):
            continue
        path=(OUT/href.split('#')[0]).resolve()
        assert path.exists(), f'Enlace roto: {name}/{href}'
        links.append({'page':name,'link':href,'exists':True})
req=Request('http://127.0.0.1:8868/research/musica-bajo-voz-2026-09-30/'+DATA['variants'][0]['mp4'],
            headers={'Range':'bytes=1024-2047'})
with urlopen(req, timeout=10) as response:
    content=response.read()
    assert response.status==206 and len(content)==1024
    assert content==(OUT/DATA['variants'][0]['mp4']).read_bytes()[1024:2048]
    ranges={'status':response.status,'content_range':response.headers['Content-Range'],
            'bytes':len(content),'byte_agreement':'pass'}
result={'status':'PASS','date_local':'2026-09-30','exports':exports,
        'pcm_voice_invariance':{'max_sfx_difference_error':error_sfx,'max_music_difference_error':error_music,
                                'limit':4e-7,'reason':'Solo cuantización PCM24, sin cambio de contribución vocal.'},
        'sfx_in_mp4':events,'music_in_mp4_correlation':music_agreement,'local_links':links,
        'http_range':ranges,'source_picture_voice_hashes':'pass',
        'human_listening':'por confirmar','audience_effect':'por confirmar',
        'ui':{'method':'CUA: tres opciones cargadas, duración19.5s/errornull, salto13.39 y comparación pausada6.99s de A a B conservada; captura de layout inspeccionada.',
              'playback_observed':True,'human_listening_by_agent':False}}
(EVID/'validacion.json').write_text(json.dumps(result, ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'aac_correlation':[x['aac_pcm_correlation'] for x in exports],
                  'sfx_correlation':[x['aac_difference_sfx_correlation'] for x in events],
                  'music_correlation':music_agreement,'links':len(links),'http_range':ranges},ensure_ascii=False))
