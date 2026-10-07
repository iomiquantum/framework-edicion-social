"""Prototipos aislados: misma imagen y voz, efectos puntuales y cama por bloques.

No edita el proyecto VIDEO-13. Requiere numpy en el runtime incluido en Codex.
"""
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1]
MEDIA = OUT / 'audiciones/practica-v1'
EVID = OUT / 'evidencia/practica-v1'
BANK = ROOT / 'Framework-Edicion-Social/library/music/candidates/2026-09-30-prueba-ritmica'
FF = '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
SR = 48000
DURATION = 19.5
N = round(DURATION * SR)
PICTURE = ROOT / 'Serie-IA-Negocios-10-Videos/VIDEO-13/editable-hyperframes-video-13/renders/VIDEO-13-FINAL.mp4'
VOICE = OUT / 'audiciones/prosodia-v2-48k/video-13-voz.wav'
MUSIC = BANK / 'neon-no-melody.mp3'
EVENTS = [
    {'id': 'apertura', 'start': .025, 'file': '04_soft_pop.wav', 'gain': .4,
     'purpose': 'Dar presencia a la afirmación inicial y a la aparición del texto.'},
    {'id': 'evidencia', 'start': 6.99, 'file': '03_ui_tick.wav', 'gain': .35,
     'purpose': 'Marcar la aparición del apoyo sobre llamadas; no cada elemento de la lista.'},
    {'id': 'valor', 'start': 13.34, 'file': '05_low_accent.wav', 'gain': .4,
     'purpose': 'Acento previo al cambio de valor; ataque dentro de la pausa medida.'},
]


def run(args, binary=False):
    p = subprocess.run(args, capture_output=True, text=not binary, timeout=100)
    if p.returncode:
        raise RuntimeError(str(p.stderr)[-1800:])
    return p


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def db(x):
    return round(20 * math.log10(max(float(x), 1e-12)), 3)


def rms(x):
    return float(np.sqrt(np.mean(np.square(x.astype(np.float64)))))


def decode(path, start=0, duration=None):
    args = [FF, '-v', 'error', '-ss', str(start), '-i', str(path), '-vn']
    if duration is not None:
        args += ['-t', str(duration)]
    # Unidad por canal: mono se duplica explícitamente, no se negocia a -3 dB.
    args += ['-af', 'aformat=channel_layouts=mono|stereo', '-ar', str(SR), '-f', 'f32le', '-']
    probe = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'a:0',
                            '-show_entries', 'stream=channels', '-of', 'json', str(path)]).stdout)
    ch = probe['streams'][0]['channels']
    x = np.frombuffer(run(args, binary=True).stdout, dtype='<f4').reshape(-1, ch).copy()
    return np.repeat(x, 2, axis=1) if ch == 1 else x


def write_pcm(x, p):
    assert np.isfinite(x).all() and float(np.max(np.abs(x))) < 1, 'Clipping antes de PCM'
    proc = subprocess.run([FF, '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2',
                           '-i', '-', '-c:a', 'pcm_s24le', '-y', str(p)],
                          input=x.astype('<f4').tobytes(), capture_output=True, timeout=60)
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode()[-1800:])


def measure(p):
    log = run([FF, '-hide_banner', '-nostats', '-i', str(p), '-vn', '-af',
               'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-']).stderr
    return json.loads(re.findall(r'\{\s*"input_i".*?\}', log, re.S)[-1])


def video_hash(p):
    return run([FF, '-v', 'error', '-i', str(p), '-map', '0:v:0', '-c:v', 'copy',
                '-f', 'hash', '-hash', 'sha256', '-']).stdout.strip()


def video_probe(p):
    return json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                           '-show_entries', 'stream=codec_name,width,height,pix_fmt,color_space,color_transfer,color_primaries,nb_frames,duration,r_frame_rate,start_time',
                           '-of', 'json', str(p)]).stdout)['streams'][0]


MEDIA.mkdir(parents=True, exist_ok=True)
EVID.mkdir(parents=True, exist_ok=True)
original_hash = sha(PICTURE)
source_video_hash = video_hash(PICTURE)
source_probe = video_probe(PICTURE)
source_html = BANK / 'licencias/neon-fuente.html'
html = source_html.read_text()
url = 'https://www.scottbuckley.com.au/library/wp-content/uploads/2019/09/sb_neon_nomelody.mp3'
assert url in html.replace('http://', 'https://') and 'Attribution 4.0' in html
run([FF, '-v', 'error', '-i', str(MUSIC), '-f', 'null', '-'])

voice = np.zeros((N, 2), np.float32)
v = decode(VOICE)
assert len(v) <= N
voice[:len(v)] = v * 10 ** (2 / 20)  # Mismo +2 dB, fijo, en las tres muestras.
effects = np.zeros_like(voice)
for e in EVENTS:
    src = ROOT / 'Framework-Edicion-Social/library/sfx' / e['file']
    x = decode(src) * e['gain']
    i = round(e['start'] * SR)
    effects[i:i+len(x)] += x
    contemporary = voice[i:i+len(x)]
    e.update(source=str(src.relative_to(ROOT)), source_sha256=sha(src),
             duration_s=len(x)/SR, peak_dbfs=db(np.max(np.abs(x))),
             rms_dbfs=db(rms(x)),
             voice_contemporary_rms_dbfs=db(rms(contemporary)),
             relative_rms_db=db(rms(x)/max(rms(contemporary), 1e-12)),
             peak_time_s=e['start']+int(np.argmax(np.abs(x).max(axis=1)))/SR)
# Equivalente acotado del guard: bindings, identidades y efecto durante el hook.
assert any(e['start'] < 2.09 and e['start'] + e['duration_s'] > 0 for e in EVENTS)
assert len({e['source_sha256'] for e in EVENTS}) >= 2
assert all(e['gain'] <= 1 for e in EVENTS)

music = np.zeros_like(voice)
bed = decode(MUSIC, start=45, duration=11.30)
start, end = 2.09, 13.39
length = round((end-start)*SR)
assert len(bed) >= length
bed = bed[:length]
segment_voice = voice[round(start*SR):round(end*SR)]
frame_rms = np.sqrt(np.mean(segment_voice[:len(segment_voice)//4800*4800].reshape(-1,4800,2)**2, axis=(1,2)))
active = frame_rms[frame_rms > frame_rms.max()*10**(-22/20)]
voice_reference = float(np.median(active))
bed_gain = voice_reference / rms(bed) * 10 ** (-18 / 20)
envelope = np.ones(length, np.float32)
attack, release = round(.30*SR), round(.70*SR)
envelope[:attack] = np.linspace(0, 1, attack)
envelope[-release:] = np.linspace(1, 0, release)
music[round(start*SR):round(end*SR)] = bed * bed_gain * envelope[:,None]
write_pcm(effects, MEDIA/'efectos-solos.wav')
write_pcm(music, MEDIA/'cama-aplicada.wav')

credit = "'Neon' by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au. " + \
         'https://www.scottbuckley.com.au/library/neon/ · https://creativecommons.org/licenses/by/4.0/.'
candidate = {'id':'BGM-CAND-SB-NEON-NOMELODY', 'title':'Neon', 'mix':'No Melody',
             'author':'Scott Buckley', 'license':'CC BY 4.0', 'license_url':'https://creativecommons.org/licenses/by/4.0/',
             'source_page':'https://www.scottbuckley.com.au/library/neon/', 'download_url':url,
             'retrieved_local':'2026-09-30', 'sha256':sha(MUSIC), 'bytes':MUSIC.stat().st_size,
             'source_html_sha256':sha(source_html), 'decode_full':'pass', 'status':'candidate_not_approved',
             'human_listening':'por confirmar', 'credit':credit,
             'reason':'Comparar un arpegio/pulso electrónico con las camas calmadas rechazadas. El carácter retro puede no encajar.',
             'changes':'Extracto45.00–56.30s, ganancia constante, fade-in0.30s/fade-out0.70s; sin cambiar la voz.'}
(BANK/'manifest.json').write_text(json.dumps(candidate, ensure_ascii=False, indent=2)+'\n')
(BANK/'CREDITOS.txt').write_text(credit+'\nCambios: '+candidate['changes']+'\n')

variants = [('00-referencia-voz', voice, 'Referencia de voz sola; no candidato de entrega final.'),
            ('01-voz-efectos', voice+effects, 'Tres acentos con tres identidades; pregunta sin cama.'),
            ('02-voz-efectos-pulso', voice+effects+music, 'Mismos efectos y pulso solo durante la explicación.')]
results=[]
for name, mix, description in variants:
    wav, mp4 = MEDIA/(name+'.wav'), MEDIA/(name+'.mp4')
    write_pcm(mix, wav)
    run([FF, '-v', 'error', '-i', str(PICTURE), '-i', str(wav), '-map', '0:v:0', '-map', '1:a:0',
         '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-t', str(DURATION), '-movflags', '+faststart', '-y', str(mp4)])
    run([FF, '-v', 'error', '-i', str(mp4), '-f', 'null', '-'])
    stats, pcm_stats = measure(mp4), measure(wav)
    assert float(stats['input_tp']) <= -1.5 and float(pcm_stats['input_tp']) <= -1.5
    vh, vp = video_hash(mp4), video_probe(mp4)
    assert vh == source_video_hash and vp == source_probe, 'Cambió la imagen/cadencia/color'
    results.append({'id':name, 'description':description, 'wav':str(wav.relative_to(OUT)),
                    'mp4':str(mp4.relative_to(OUT)), 'wav_sha256':sha(wav), 'mp4_sha256':sha(mp4),
                    'pcm_loudness':pcm_stats, 'aac_loudness':stats, 'video_stream_hash':vh,
                    'video_probe':vp, 'full_decode':'pass'})
    print(name, stats['input_i'], 'LUFS', stats['input_tp'], 'dBTP; imagen idéntica', flush=True)

assert sha(PICTURE) == original_hash
manifest={'date_local':'2026-09-30', 'scope':'Pruebas aisladas de investigación, sin editar VIDEO-13 ni adoptarlas como final.',
          'status':'technical_pass_pending_user_listening', 'human_listening':'por confirmar',
          'picture_source':str(PICTURE.relative_to(ROOT)), 'picture_source_sha256':original_hash,
          'voice_source':str(VOICE.relative_to(ROOT)), 'voice_source_sha256':sha(VOICE),
          'voice_gain_db':2, 'voice_processing_added':'Ninguno: ganancia constante común y duplicación mono unity L/R.',
          'sample_rate':SR, 'duration_s':DURATION, 'sfx_events':EVENTS,
          'music':{'candidate':candidate['id'], 'source_sha256':sha(MUSIC), 'source_range_s':[45,56.3],
                   'timeline_s':[start,end], 'gain':bed_gain, 'fade_in_s':.30, 'fade_out_s':.70,
                   'calibration':'RMS estéreo sin fade18dB bajo mediana de voz activa en ventanas100ms del bloque.',
                   'voice_reference_rms_dbfs':db(voice_reference), 'applied_bed_rms_dbfs':db(rms(music[round(start*SR):round(end*SR)]))},
          'mix_method':'Suma de stems float32, sin normalización por variante, compresión ni limiter. Voz idéntica en PCM; AAC se codifica independientemente.',
          'guard':{'hook_present':True, 'distinct_sfx_identities':3, 'source_links_hashes':'pass'},
          'variants':results, 'original_unchanged':True,
          'limits':['Métricas no prueban audibilidad/inteligibilidad, efecto sobre atención ni aceptación.',
                    'No se ha realizado escucha por el agente; revisar las muestras completas y en teléfono.',
                    'No se ha aplicado esta decisión al editable; si se adopta debe trasladarse a su grafo y validar su export.']}
(EVID/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print('QA técnico PASS. Escucha y selección por confirmar.', flush=True)
