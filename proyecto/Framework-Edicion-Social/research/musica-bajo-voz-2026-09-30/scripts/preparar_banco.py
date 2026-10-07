"""Descarga autorizada desde el compositor y muestras locales de investigación."""
import array
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parents[1]
BANK=ROOT/'Framework-Edicion-Social/library/music/candidates/2026-09-30'
FFMPEG='/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
BANK.mkdir(parents=True,exist_ok=True)
(BANK/'licencias').mkdir(exist_ok=True)
(OUT/'audiciones').mkdir(exist_ok=True)

TRACKS=[
 {'id':'BGM-CAND-SB-COMPUTATIONS-NOCELLO','title':'Computations in a Snowstorm',
  'mix':'No Cello','slug':'computations','file':'computations-no-cello.mp3',
  'url':'https://www.scottbuckley.com.au/library/wp-content/uploads/2019/01/sb_computations_altmix.mp3',
  'fit':'Candidato ambiental para procesos de IA; confirmar que el tono no resulte demasiado oscuro.'},
 {'id':'BGM-CAND-SB-INTERVENTION-NOMELODY','title':'Intervention',
  'mix':'No Piano Melody','slug':'intervention','file':'intervention-no-piano-melody.mp3',
  'url':'https://www.scottbuckley.com.au/library/wp-content/uploads/2019/01/sb_intervention_nomelody.mp3',
  'fit':'Candidato para una advertencia o tensión breve; no imponer suspense a toda explicación.'},
 {'id':'BGM-CAND-SB-CIRRUS','title':'Cirrus',
  'mix':'Full Mix','slug':'cirrus','file':'cirrus.mp3',
  'url':'https://www.scottbuckley.com.au/library/wp-content/uploads/2023/03/Cirrus.mp3',
  'fit':'Candidato para reflexión humana; comprobar que la emoción no domine el mensaje.'}
]

def run(args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=100)
 if p.returncode: raise RuntimeError(p.stderr[-1600:])
 return p

def fetch(url,path):
 if not path.exists():
  run(['/usr/bin/curl','--fail','--location','--retry','1','--max-time','40',url,'--output',str(path)])
 if not path.stat().st_size: raise RuntimeError('Descarga vacía: '+str(path))

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def measure(path):
 p=run([FFMPEG,'-hide_banner','-nostats','-i',str(path),'-vn','-af',
        'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
 blobs=re.findall(r'\{\s*"input_i".*?\}',p.stderr,re.S)
 return json.loads(blobs[-1])

def rms(path):
 p=subprocess.run([FFMPEG,'-v','error','-i',str(path),'-ac','2','-ar','48000','-f','f32le','-'],capture_output=True,timeout=60)
 if p.returncode: raise RuntimeError(p.stderr.decode())
 a=array.array('f'); a.frombytes(p.stdout)
 return math.sqrt(sum(v*v for v in a)/len(a))

records=[]
for tr in TRACKS:
 page='https://www.scottbuckley.com.au/library/'+tr['slug']+'/'
 evidence=BANK/'licencias'/f"{tr['slug']}-fuente.html"
 fetch(page,evidence)
 html=evidence.read_text()
 if tr['url'] not in html.replace('http://','https://') or 'Attribution 4.0' not in html:
  raise RuntimeError('La página no confirma enlace/licencia de '+tr['title'])
 dst=BANK/tr['file']; fetch(tr['url'],dst)
 probe=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(dst)]).stdout)
 # Decode completo independiente de la medición para detectar archivo truncado.
 run([FFMPEG,'-v','error','-i',str(dst),'-f','null','-'])
 preview=OUT/'audiciones'/f"{tr['slug']}-musica-sola-20s.mp3"
 run([FFMPEG,'-v','error','-ss','45','-i',str(dst),'-t','20','-af',
      'afade=t=in:st=0:d=0.35,afade=t=out:st=19:d=1','-c:a','libmp3lame','-b:a','192k','-y',str(preview)])
 credit=f"'{tr['title']}' by Scott Buckley – released under CC-BY 4.0. www.scottbuckley.com.au. Fuente: {page} Licencia: https://creativecommons.org/licenses/by/4.0/."
 rec={**tr,'author':'Scott Buckley','source_page':page,'license':'CC BY 4.0',
      'license_url':'https://creativecommons.org/licenses/by/4.0/',
      'retrieved_at_local':'2026-09-30','status':'candidate','human_listening':'por confirmar',
      'download_path':str(dst.relative_to(ROOT)),'bytes':dst.stat().st_size,'sha256':sha(dst),
      'source_html_sha256':sha(evidence),'duration_s':float(probe['format']['duration']),
      'audio_stream':probe['streams'][0],'loudness':measure(dst),
      'decode_full':'pass','credit':credit,'preview':str(preview.relative_to(ROOT)),
      'allowed_scope':'Uso comercial y adaptación según CC BY 4.0, con atribución y registro de cambios.',
      'creator_notes':'En YouTube el compositor pide crédito en descripción. No registrar en Content ID ni subir como música aislada. Ver copia de condiciones.'}
 records.append(rec)
 (BANK/'manifest.json').write_text(json.dumps({'tracks':records},ensure_ascii=False,indent=2))
 print(tr['title'],round(rec['duration_s'],2),'s; descarga, licencia y decode PASS',flush=True)

fetch('https://www.scottbuckley.com.au/library/using-this-music/',BANK/'licencias/condiciones-compositor.html')
fetch('https://creativecommons.org/licenses/by/4.0/',BANK/'licencias/cc-by-4.0.html')

# Audiciones de doce segundos, fuera de las composiciones y renders existentes.
source=ROOT/'Serie-IA-Negocios-10-Videos/VIDEO-13/editable-hyperframes-video-13/assets/video13-voice-normalized-v1.m4a'
voice=OUT/'audiciones/00-voz-sola-video13-12s.wav'
run([FFMPEG,'-v','error','-i',str(source),'-t','12','-ar','48000','-ac','2','-c:a','pcm_s24le','-y',str(voice)])
voice_rms=rms(voice)
audition={'source':str(source.relative_to(ROOT)),'source_sha256':sha(source),
          'voice_clip':str(voice.relative_to(ROOT)),'voice_clip_sha256':sha(voice),
          'range_source_s':[0,12],'voice_rms_dbfs':20*math.log10(voice_rms),
          'method':'Misma voz sin cambio de ganancia. Cama a 24 dB menos de RMS medio del fragmento; fades solo en música. Sin normalización por variante. No es verificación perceptual ni cumplimiento WCAG.',
          'human_listening':'por confirmar','mixes':[]}
bed_specs=[('01-tech-original',ROOT/'Framework-Edicion-Social/library/music/tech_pulse_114bpm_8bars.wav',0)]
bed_specs += [(f"{i+2:02d}-{t['slug']}",BANK/t['file'],45) for i,t in enumerate(TRACKS)]
for name,src,start in bed_specs:
 bed=OUT/'audiciones'/f'{name}-cama-12s.wav'
 run([FFMPEG,'-v','error','-ss',str(start),'-i',str(src),'-t','12','-ar','48000','-ac','2','-c:a','pcm_s24le','-y',str(bed)])
 gain=(voice_rms/rms(bed))*10**(-24/20)
 mix=OUT/'audiciones'/f'{name}-bajo-voz-video13-12s.wav'
 filters=f'[1:a]volume={gain:.12f},afade=t=in:st=0:d=0.35,afade=t=out:st=11:d=1[bed];[0:a][bed]amix=inputs=2:duration=first:normalize=0[mix]'
 run([FFMPEG,'-v','error','-i',str(voice),'-i',str(bed),'-filter_complex',filters,'-map','[mix]','-c:a','pcm_s24le','-y',str(mix)])
 audition['mixes'].append({'name':name,'bed_source':str(src.relative_to(ROOT)),
                          'bed_source_start_s':start,'music_gain':gain,'music_gain_db':20*math.log10(gain),
                          'file':str(mix.relative_to(ROOT)),'sha256':sha(mix),'loudness':measure(mix)})
print('Voz sola y cuatro comparaciones bajo voz preparadas.',flush=True)
(OUT/'evidencia/audiciones.json').write_text(json.dumps(audition,ensure_ascii=False,indent=2))
(BANK/'CREDITOS.txt').write_text('\n\n'.join(r['credit']+'\nSi se usa un extracto o se ajusta el volumen: indicar fragmento editado, fundidos y nivel ajustado.' for r in records)+'\n')
