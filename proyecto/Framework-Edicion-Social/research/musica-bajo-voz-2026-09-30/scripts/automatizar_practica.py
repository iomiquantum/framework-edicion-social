"""D: automatización editorial de la cama; conserva C y su comienzo."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parents[1]
DEST=OUT/'audiciones/practica-v2'
EVID=OUT/'evidencia/practica-v2'
FF='/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
SR=48000;N=round(19.5*SR)


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):return subprocess.run(args,capture_output=True,text=True,check=True,timeout=100)
def decode(p):
    r=subprocess.run([FF,'-v','error','-i',str(p),'-ar',str(SR),'-ac','2','-f','f32le','-'],capture_output=True,check=True)
    return np.frombuffer(r.stdout,'<f4').reshape(-1,2)[:N].copy()
def write(x,p):
    assert float(np.abs(x).max())<1
    r=subprocess.run([FF,'-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','-',
                       '-c:a','pcm_s24le','-y',str(p)],input=x.astype('<f4').tobytes(),capture_output=True)
    assert r.returncode==0,r.stderr.decode()
def measure(p):
    s=run([FF,'-hide_banner','-nostats','-i',str(p),'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr
    return json.loads(re.findall(r'\{\s*"input_i".*?\}',s,re.S)[-1])

DEST.mkdir(parents=True,exist_ok=True);EVID.mkdir(parents=True,exist_ok=True)
base=OUT/'audiciones/practica-v1'
voice=decode(base/'00-referencia-voz.wav');sfx=decode(base/'efectos-solos.wav');bed=decode(base/'cama-aplicada.wav')
# Ganancias relativas a la cama C ya fundida; interpolación en dB, sin seguir sílabas.
points=[(0,0),(4.05,0),(4.35,-4),(4.70,-4),(5.10,-2),(5.32,-6),
        (6.78,-6),(7.00,-2.5),(7.25,-4.5),(8.80,-4.5),(9.00,-6),
        (9.45,-5),(10.10,-5),(10.65,-5.5),(13.39,-5.5),(19.5,-5.5)]
time=np.arange(N)/SR
gain_db=np.interp(time,[x[0] for x in points],[x[1] for x in points])
new_bed=bed*10**(gain_db[:,None]/20)
mix=voice+sfx+new_bed
wav=DEST/'03-voz-efectos-pulso-automatizado.wav';mp4=DEST/'03-voz-efectos-pulso-automatizado.mp4'
write(new_bed,DEST/'cama-automatizada.wav');write(mix,wav)
picture=ROOT/'Serie-IA-Negocios-10-Videos/VIDEO-13/editable-hyperframes-video-13/renders/VIDEO-13-FINAL.mp4'
picture_hash=sha(picture)
run([FF,'-v','error','-i',str(picture),'-i',str(wav),'-map','0:v:0','-map','1:a:0',
     '-c:v','copy','-c:a','aac','-b:a','256k','-t','19.5','-movflags','+faststart','-y',str(mp4)])
run([FF,'-v','error','-i',str(mp4),'-f','null','-'])
pcml, aacl=measure(wav),measure(mp4)
assert float(aacl['input_tp'])<=-1.5 and float(pcml['input_tp'])<=-1.5
video_hash=lambda p:run([FF,'-v','error','-i',str(p),'-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256','-']).stdout.strip()
assert video_hash(mp4)==video_hash(picture) and sha(picture)==picture_hash
pcm=decode(wav);aac=decode(mp4);before=decode(base/'02-voz-efectos-pulso.wav')
prefix_error=float(np.abs(pcm[:round(4.05*SR)]-before[:round(4.05*SR)]).max())
invariance=float(np.abs((pcm-decode(DEST/'cama-automatizada.wav'))-(voice+sfx)).max())
assert prefix_error<4e-7 and invariance<4e-7
agreement=float(np.corrcoef(pcm.ravel(),aac.ravel())[0,1]);assert agreement>.995
record={'status':'technical_pass_pending_user_review','date_local':'2026-09-30',
        'purpose':'Respuesta al feedback de C: inicio gusta, falta bajar música por momentos para conservar mensaje.',
        'id':'03-voz-efectos-pulso-automatizado','wav':str(wav.relative_to(OUT)),'mp4':str(mp4.relative_to(OUT)),
        'wav_sha256':sha(wav),'mp4_sha256':sha(mp4),'pcm_loudness':pcml,'aac_loudness':aacl,
        'envelope_relative_to_C_db':points,'interpolation':'Lineal en dB; rides por frase, sin bombeo sílaba a sílaba.',
        'beginning_identical_pcm_until_s':4.05,'beginning_max_error':prefix_error,
        'voice_sfx_invariance_max_error':invariance,'aac_pcm_correlation':agreement,
        'image_stream_unchanged':True,'picture_source_sha256':picture_hash,
        'voices_sfx_changed':False,'new_voice_fx':False,'C_preserved':True,
        'sources':{str(p.relative_to(OUT)):sha(p) for p in [base/'00-referencia-voz.wav',base/'efectos-solos.wav',base/'cama-aplicada.wav']},
        'scope':'Prueba aislada, no sustituye editable/entrega13; sin incorporar música de referencia.',
        'human_listening':'por confirmar','limits':['Los tiempos de palabras no son alineación fonética; revisar dentro del video.',
                                                   'Reducciones4–6dB son decisiones de prueba, no faders copiados de la referencia ni aprobación.']}
(EVID/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':record['status'],'LUFS':aacl['input_i'],'dBTP':aacl['input_tp'],
                  'prefix_error':prefix_error,'voice_sfx_error':invariance,'aac_correlation':agreement}))
