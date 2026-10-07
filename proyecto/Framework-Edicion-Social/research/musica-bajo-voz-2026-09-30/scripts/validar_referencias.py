"""QA de originales, derivados y automatización. No certifica escucha ni stems puros."""
import hashlib
import importlib.metadata
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import soundfile as sf

OUT = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def run(args):
    p = subprocess.run(args, capture_output=True, timeout=120)
    assert p.returncode == 0, p.stderr.decode(errors='replace')
    return p.stdout


def packet_hash(path, kind):
    return run([FF, '-v', 'error', '-i', str(path), '-map', kind,
                '-c', 'copy', '-f', 'hash', '-hash', 'sha256', '-']).decode().strip()


def pcm(path, rate):
    return np.frombuffer(run([FF, '-v', 'error', '-i', str(path), '-vn', '-ar', str(rate),
                              '-ac', '2', '-f', 'f32le', '-']), '<f4').reshape(-1, 2).copy()


refs = []
for ident in ['ref-01', 'ref-02']:
    folder = OUT / 'referencias-usuario' / ident
    profile = json.loads((folder / 'perfil-mezcla.json').read_text())
    separation = json.loads((folder / 'separacion.json').read_text())
    source, preview = Path(profile['source']), folder / 'preview.mp4'
    assert sha(source) == profile['source_sha256'], 'Original modificado'
    hashes = [packet_hash(p, '0:a:0') for p in [source, preview]]
    assert hashes[0] == hashes[1], 'El preview cambió los paquetes AAC'
    for p in [source, preview]:
        run([FF, '-v', 'error', '-i', str(p), '-f', 'null', '-'])
    mix, rate = sf.read(folder / 'mezcla.wav', dtype='float32', always_2d=True)
    decoded = pcm(source, rate)
    assert decoded.shape == mix.shape and rate == 44100
    error = float(np.max(np.abs(decoded - mix)))
    assert error < 3e-7, 'Extracción cambió la ganancia más allá de PCM24'
    summed = np.zeros_like(mix)
    stem_checks = []
    for s in separation['stems']:
        path = folder / s['path']
        data, sr = sf.read(path, dtype='float32', always_2d=True)
        assert sha(path) == s['sha256'] and sr == rate and data.shape == mix.shape
        assert np.isfinite(data).all() and sf.info(path).subtype == 'FLOAT'
        summed += data
        stem_checks.append({'name': s['name'], 'hash_shape_finite_float': 'PASS'})
    reconstruction = float(np.corrcoef(mix.reshape(-1), summed.reshape(-1))[0, 1])
    assert reconstruction > .995
    duration = float(profile['probe']['format']['duration'])
    blocks = profile['blocks']
    assert all(0 <= b['start_s'] < b['end_s'] <= duration + .02 for b in blocks)
    transcription = json.loads((folder / 'transcripcion.json').read_text())['transcription']
    assert all(0 <= t['offsets']['from'] <= t['offsets']['to'] <= duration * 1000 + 200
               for t in transcription)
    refs.append({'id': ident, 'source': str(source), 'source_sha256': sha(source),
                 'source_unchanged': True, 'source_preview_full_decode': 'PASS',
                 'preview_audio_packets_identical': True, 'aac_payload_hash': hashes[0],
                 'audio_extraction_max_pcm_error': error, 'blocks_in_range': len(blocks),
                 'asr_segments_in_range': len(transcription), 'stems': stem_checks,
                 'reconstruction_correlation_consistency_only': reconstruction,
                 'dense_frames_generated': len(list((folder / 'frames-2fps').glob('*.jpg'))),
                 'human_listening_by_agent': False})
    print(ident, 'PASS', len(blocks), 'blocks', flush=True)

v1 = json.loads((OUT / 'evidencia/practica-v1/manifest.json').read_text())
v2 = json.loads((OUT / 'evidencia/practica-v2/manifest.json').read_text())
c_record = next(x for x in v1['variants'] if x['id'] == '02-voz-efectos-pulso')
assert sha(OUT / c_record['mp4']) == c_record['mp4_sha256']
assert sha(ROOT / v1['picture_source']) == v1['picture_source_sha256']
for ext in ['wav', 'mp4']:
    assert sha(OUT / v2[ext]) == v2[ext + '_sha256']
for name, digest in v2['sources'].items():
    assert sha(OUT / name) == digest
d = pcm(OUT / v2['wav'], 48000)
c = pcm(OUT / c_record['wav'], 48000)
voice = pcm(OUT / 'audiciones/practica-v1/00-referencia-voz.wav', 48000)
sfx = pcm(OUT / 'audiciones/practica-v1/efectos-solos.wav', 48000)
bed = pcm(OUT / 'audiciones/practica-v2/cama-automatizada.wav', 48000)
prefix_error = float(np.max(np.abs(d[:round(4.05*48000)] - c[:round(4.05*48000)])))
voice_error = float(np.max(np.abs(d - bed - sfx - voice)))
assert prefix_error < 4e-7 and voice_error < 4e-7
aac = pcm(OUT / v2['mp4'], 48000)[:len(d)]
agreement = float(np.corrcoef(d.reshape(-1), aac.reshape(-1))[0, 1])
assert agreement > .995
picture_hashes = [packet_hash(p, '0:v:0') for p in [ROOT / v1['picture_source'], OUT / v2['mp4']]]
assert picture_hashes[0] == picture_hashes[1]
run([FF, '-v', 'error', '-i', str(OUT / v2['mp4']), '-f', 'null', '-'])

# QA.json es el resultado de esta misma comprobación; se escribe al finalizar.
target = OUT / 'referencias-usuario/validacion.json'
links = []
for name in ['practica.html', 'referencias.html']:
    for href in re.findall(r'(?:href|src)="([^"]+)"', (OUT / name).read_text()):
        if urlparse(href).scheme or href.startswith('#'):
            continue
        path = (OUT / href.split('#')[0]).resolve()
        assert path.exists() or path == target, f'Enlace roto {name}/{href}'
        links.append({'page': name, 'href': href, 'exists': True})

result = {'status': 'TECHNICAL_PASS', 'date_local': '2026-09-30', 'references': refs,
          'D': {'C_preserved': True, 'picture_source_unchanged': True,
                'picture_payload_identical': True, 'prefix_4_05_s_pcm_error': prefix_error,
                'voice_sfx_invariance_pcm_error': voice_error, 'aac_pcm_correlation': agreement,
                'full_decode': 'PASS', 'user_listening': 'por confirmar'},
          'local_links': links,
          'runtime_packages': {n: importlib.metadata.version(n) for n in
                               ['demucs', 'torch', 'torchaudio', 'numpy', 'soundfile']},
          'limits': ['Separación aproximada; consistencia de suma no demuestra pureza de stems.',
                     'ASR por frase es provisional; no certifica palabras ni alineación fonética.',
                     'Nombres de canciones/SFX y faders originales por confirmar.',
                     'Reproducción técnica no equivale a escucha humana ni aprobación.']}
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': result['status'], 'references': len(refs),
                  'blocks': sum(x['blocks_in_range'] for x in refs), 'D': result['D']}, ensure_ascii=False))
