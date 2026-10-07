"""Mapa temporal de mezcla y estimaciones; no identifica faders originales."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

OUT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--ref',default='ref-01');args=parser.parse_args()
REF=OUT/'referencias-usuario'/args.ref
SOURCE=Path('/Users/iomijhondavid/Downloads')/{'ref-01':'65B73BD5-A22A-4DC4-A9C5-D132C7C03C04.MP4','ref-02':'31DAFCE4-1F8C-452E-B66D-489909CDBF67.MP4'}[args.ref]
FF='/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
probe=json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(SOURCE)],capture_output=True,text=True,check=True).stdout)
offset=float(next(s['start_time'] for s in probe['streams'] if s['codec_type']=='audio'))
mix,sr=sf.read(REF/'mezcla.wav',dtype='float32',always_2d=True)
voice,_=sf.read(REF/'estimaciones-demucs/vocals.wav',dtype='float32',always_2d=True)
music,_=sf.read(REF/'estimaciones-demucs/acompanamiento-estimado.wav',dtype='float32',always_2d=True)
assert mix.shape==voice.shape==music.shape
hop=round(.10*sr);n=len(mix)//hop
t=(np.arange(n)+.5)*hop/sr+offset


def level(x):
    energy=np.mean(x[:n*hop].reshape(n,hop,2).astype(np.float64)**2,axis=(1,2))
    return 10*np.log10(np.maximum(energy,1e-14))


def band_level(x,lo,hi):
    frames=x[:n*hop].reshape(n,hop,2).astype(np.float64)
    f=np.fft.rfftfreq(hop,1/sr);z=np.fft.rfft(frames,axis=1)
    z[:,(f<lo)|(f>=hi)]=0
    return 10*np.log10(np.maximum(np.mean(np.fft.irfft(z,n=hop,axis=1)**2,axis=(1,2)),1e-14))


ml,vl,bl=level(mix),level(voice),level(music)
vband,bband=band_level(voice,350,5000),band_level(music,350,5000)
threshold=float(np.percentile(vl,90)-25)
active=vl>threshold
raw_blocks=[
 (0,1.68,'Fragmento inicial / continuidad de la grabación'),
 (1.68,5.64,'Portero y automatización'),
 (5.64,9.28,'Presentación del invitado'),
 (9.28,16.04,'Quién es Jamilton'),
 (16.04,19.60,'Reacción y pregunta por el nombre'),
 (19.60,27.22,'Brian y remate del nombre'),
 (27.22,31.32,'Cuenta de Amazon y servos'),
 (31.32,36.98,'Aseo gratis y teleoperación'),
 (36.98,42.64,'Cámara y conversaciones privadas'),
 (42.64,48.18,'Respuesta con voz de robot'),
 (48.18,56.68,'Hermano y cigarrillos: remate humorístico'),
 (56.68,60.56,'Robot para el hijo'),
 (60.56,67.60,'Marca y llamada al canal'),
 (67.60,len(mix)/sr,'Final de captura / posible repetición'),
]
if (REF/'mapa-editorial.json').exists():
    raw_blocks=[(b['start'],b['end'],b['label']) for b in json.loads((REF/'mapa-editorial.json').read_text())['blocks']]
blocks=[]
for a,b,label in raw_blocks:
    mask=(t>=a+offset)&(t<b+offset);talk=mask&active
    row={'start_s':round(a+offset,3),'end_s':round(b+offset,3),'label':label,
         'mix_rms_median_dbfs':float(np.median(ml[mask])),
         'estimated_voice_rms_median_dbfs':float(np.median(vl[mask])),
         'estimated_accompaniment_rms_median_dbfs':float(np.median(bl[mask])),
         'estimated_active_voice_fraction':float(np.mean(active[mask]))}
    if talk.any():
        dif=bl[talk]-vl[talk]
        row['accompaniment_vs_voice_db_p10_median_p90']=[float(x) for x in np.percentile(dif,[10,50,90])]
        row['band350_5000_accompaniment_vs_voice_median_db']=float(np.median(bband[talk]-vband[talk]))
    if 42.64<=a<48.18:
        row['separation_caution']='Voz robótica: puede distribuirse entre vocals/accompaniment; no interpretar como fader.'
    blocks.append(row)

# Eventos rápidos son candidatos a revisar, no efectos identificados por escucha.
delta=np.diff(bl,prepend=bl[0]);candidates=[]
for i in np.argsort(delta)[::-1]:
    if delta[i]<5 or bl[i]<-38 or any(abs(float(t[i])-x['time_s'])<.7 for x in candidates):
        continue
    candidates.append({'time_s':round(float(t[i]),3),'accompaniment_rise_100ms_db':round(float(delta[i]),2),
                       'accompaniment_rms_dbfs':round(float(bl[i]),2),
                       'status':'transient_candidate_music_sfx_or_leakage_not_classified'})
    if len(candidates)==16:
        break
candidates.sort(key=lambda x:x['time_s'])

fig,axs=plt.subplots(2,1,figsize=(15,6),sharex=True,gridspec_kw={'height_ratios':[2,1]})
axs[0].plot(t,vl,color='#146c5c',linewidth=1,label='Voz estimada')
axs[0].plot(t,bl,color='#b65d29',linewidth=1,label='Acompañamiento estimado (música/SFX/residuos)')
axs[0].set_ylim(-70,-4);axs[0].set_ylabel('RMS dBFS / 100 ms');axs[0].legend(loc='lower left',fontsize=9)
ratio=np.where(active,bl-vl,np.nan)
axs[1].plot(t,ratio,color='#405895',linewidth=.8)
axs[1].axhline(0,color='grey',linestyle='--',linewidth=.8)
axs[1].set_ylim(-38,15);axs[1].set_ylabel('Acomp. − voz / dB');axs[1].set_xlabel('Tiempo en la grabación de pantalla / segundos')
for ax in axs:
    ax.grid(alpha=.18)
    for b in blocks[1:]:
        ax.axvline(b['start_s'],color='grey',alpha=.23,linewidth=.6)
fig.suptitle(f'Referencia {args.ref[-2:]} · Cambios de relación entre voz y acompañamiento\nSeparación aproximada: no son pistas ni automatizaciones originales',fontsize=12)
fig.tight_layout();fig.savefig(REF/'niveles-estimados.png',dpi=150);plt.close(fig)

# Comparación propia: stems exactos, por tanto sin la incertidumbre del separador.
def decode48(p):
    r=subprocess.run([FF,'-v','error','-i',str(p),'-ar','48000','-ac','2','-f','f32le','-'],capture_output=True,check=True)
    return np.frombuffer(r.stdout,'<f4').reshape(-1,2).copy()

cvoice=decode48(OUT/'audiciones/practica-v1/00-referencia-voz.wav')
cbed=decode48(OUT/'audiciones/practica-v1/cama-aplicada.wav')
cn=len(cvoice)//4800;ct=(np.arange(cn)+.5)*.1
cv=10*np.log10(np.maximum(np.mean(cvoice[:cn*4800].reshape(cn,4800,2)**2,axis=(1,2)),1e-14))
cb=10*np.log10(np.maximum(np.mean(cbed[:cn*4800].reshape(cn,4800,2)**2,axis=(1,2)),1e-14))
cthr=float(np.percentile(cv,90)-22);cm=(ct>=2.39)&(ct<12.69)&(cv>cthr)
risk=(cb-cv>-12)&cm
candidates_c=[{'time_s':round(float(ct[i]),2),'voice_rms_dbfs':round(float(cv[i]),2),
                'music_rms_dbfs':round(float(cb[i]),2),'music_vs_voice_db':round(float(cb[i]-cv[i]),2)} for i in np.flatnonzero(risk)]
result={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'probe':probe,'audio_to_video_offset_s':offset,'method':'Demucs estimado, RMS estéreo por100ms, banda350–5000FFT, actividad relativa p90−25dB.',
        'voice_activity_threshold_dbfs':threshold,'blocks':blocks,'transient_candidates':candidates,
        'series':{'time_s':t.round(4).tolist(),'voice_estimated_rms_dbfs':vl.round(2).tolist(),
                  'accompaniment_estimated_rms_dbfs':bl.round(2).tolist(),'mix_rms_dbfs':ml.round(2).tolist()},
        'practice_C':{'method':'Stems propios exactos: RMS100ms, voz activa p90−22dB; umbral de revisión de relación−12dB, no norma de mezcla.',
                      'review_windows':candidates_c,'music_automation_current':'Ganancia constante y fundidos2.09–2.39/12.69–13.39; sin rides por frase.'},
        'limits':['No hubo escucha del agente; percepción del carácter o efectos exactos por confirmar.',
                  'Un cambio de energía puede venir de instrumentación, dinámica de la pista, efectos o automatización: no identifica un fader.',
                  'ASR reutilizado para segmentar ideas, con nombres/último tramo dudosos; capturas de la pantalla inspeccionadas.',
                  'Sin stems originales no se identifica número de canciones ni ajuste exacto de cada pista.']}
(REF/'perfil-mezcla.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
for b in blocks:
    rel=b.get('accompaniment_vs_voice_db_p10_median_p90',[0,0,0])[1]
    print(f"{b['start_s']:5.2f}–{b['end_s']:5.2f} {b['label']}: voz{b['estimated_voice_rms_median_dbfs']:6.1f}, acomp{b['estimated_accompaniment_rms_median_dbfs']:6.1f}, relación activa{rel:6.1f}dB")
print('C: ventanas para revisar',candidates_c)
