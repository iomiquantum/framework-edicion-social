"""Descargas oficiales acotadas. Catálogo curado por función, sin aprobación automática."""
import hashlib
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]
FW = OUT.parents[1]
DEST = FW / 'library/music/candidates/2026-09-30-funciones'
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
DEST.mkdir(parents=True, exist_ok=True)
(DEST/'licencias').mkdir(exist_ok=True)
items = [
    {'id': 'BGM-CAND-SB-RESONANCE-ALT', 'title': 'Resonance', 'mix': 'No Melody in Backend',
     'slug': 'resonance', 'url': 'https://www.scottbuckley.com.au/library/wp-content/uploads/2018/04/sb_resonance_altmix.mp3',
     'file': 'resonance-no-backend-melody.mp3', 'roles': ['curiosidad', 'tension', 'contraste'],
     'description': 'El compositor describe pulso electrónico, guitarras ambientales y desarrollo de sintetizadores más intenso.',
     'caution': 'Carácter oscuro/industrial. No usar como fondo genérico; revisar actividad y palabras suaves.', 'start': 20},
    {'id': 'BGM-CAND-SB-SARSAPARILLA', 'title': 'Sarsaparilla', 'mix': 'Full Mix',
     'slug': 'sarsaparilla', 'url': 'https://www.scottbuckley.com.au/wp-content/audio/sb_sarsaparilla.mp3',
     'file': 'sarsaparilla.mp3', 'roles': ['impulso', 'ejemplo', 'solucion'],
     'description': 'El compositor describe pop luminoso con percusión, guitarra y sintetizadores.',
     'caution': 'Arreglo denso y sin mezcla alternativa. Puede competir con la voz; candidato para probar, no elección final.', 'start': 40},
]


def run(args):
    p = subprocess.run(args, capture_output=True, timeout=120)
    assert p.returncode == 0, p.stderr.decode(errors='replace')
    return p.stdout


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


for t in items:
    page = 'https://www.scottbuckley.com.au/library/'+t['slug']+'/'
    html = DEST/'licencias'/(t['slug']+'-fuente.html')
    if not html.exists():
        run(['curl', '-fsSL', '--max-time', '60', page, '-o', str(html)])
    content = html.read_text()
    assert 'creativecommons.org/licenses/by/4.0' in content
    assert t['url'].replace('https:', 'http:') in content or t['url'] in content
    path = DEST/t['file']
    if not path.exists():
        run(['curl', '-fsSL', '--max-time', '120', t['url'], '-o', str(path)])
    run([FF, '-v', 'error', '-i', str(path), '-f', 'null', '-'])
    probe = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))
    preview = OUT/'audiciones/biblioteca-funciones'/(t['slug']+'-20s.wav')
    preview.parent.mkdir(exist_ok=True)
    # Normalización por ganancia fija, calculada sobre el extracto; sin compresión.
    measurement = subprocess.run([FF, '-hide_banner', '-ss', str(t['start']), '-i', str(path),
                                  '-t', '20', '-af', 'loudnorm=I=-20:TP=-1:LRA=11:print_format=json',
                                  '-f', 'null', '-'], capture_output=True, timeout=60)
    assert measurement.returncode == 0
    log = measurement.stderr.decode()
    stats = json.loads(log[log.rfind('{'):log.rfind('}')+1])
    gain = -20-float(stats['input_i'])
    run([FF, '-v', 'error', '-y', '-ss', str(t['start']), '-i', str(path), '-t', '20',
         '-af', f'volume={gain}dB,afade=t=in:d=0.1,afade=t=out:st=19.5:d=0.5',
         '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s24le', str(preview)])
    run([FF, '-v', 'error', '-i', str(preview), '-f', 'null', '-'])
    t.update({'author': 'Scott Buckley', 'license': 'CC BY 4.0',
              'license_url': 'https://creativecommons.org/licenses/by/4.0/',
              'source_page': page, 'retrieved_local': '2026-09-30',
              'sha256': sha(path), 'bytes': path.stat().st_size,
              'source_html_sha256': sha(html), 'source_html': str(html.relative_to(FW)),
              'duration_s': float(probe['format']['duration']),
              'file': str(path.relative_to(FW)), 'decode_full': 'PASS',
              'status': 'candidate_not_listened', 'human_listening': 'por confirmar',
              'credit': f"'{t['title']}' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au. {page} · https://creativecommons.org/licenses/by/4.0/.",
              'preview': str(preview.relative_to(FW)), 'preview_sha256': sha(preview),
              'preview_changes': {'source_start_s': t['start'], 'duration_s': 20, 'constant_gain_db': gain,
                                  'fade_in_s': .1, 'fade_out_s': .5, 'compression': False}})
    print(t['title'], 'download/decode/hash PASS', flush=True)

(DEST/'manifest.json').write_text(json.dumps({'date_local':'2026-09-30','tracks':items,
    'selection_basis':'Descripciones primarias y función editorial propuesta; encaje auditivo por confirmar.',
    'fallback':'Inventario local revisado. HeyGen CLI no disponible en investigación previa; fuentes oficiales con licencia verificable.',
    'recovery':'urllib Python del sistema carecía de CA local; curl con validación TLS permitió descargas, sin desactivar SSL.'},ensure_ascii=False,indent=2)+'\n')
(DEST/'CREDITOS.txt').write_text('\n\n'.join(t['credit']+'\nEn previews: extracto, ganancia fija y fundidos.' for t in items)+'\n')
(DEST/'README.md').write_text('# Candidatos por función\n\nDos descargas oficiales con CC BY 4.0 y atribución. Pendientes de escuchar con voz real. No proceden de las referencias del usuario. Los títulos y roles son propuestas; no se certifica adecuación ni se adoptan en entregas.\n\nVer manifest.json para hashes, procedencia, versiones, previews y cambios; CREDITOS.txt para reutilización.\n')
