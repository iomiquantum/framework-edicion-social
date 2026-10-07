"""Two reversible editorial hypotheses informed by context and estimates, not automatic model approval."""
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy import signal
import soundfile as sf

from evaluar_indices import OUT, BANK, FS, FFMPEG, read_audio, indices

PLANS = {
 "largo-53": {
   "music_db": [[0,0],[.45,2.5],[2.85,2.5],[3.15,0],[4.85,0],[5.35,2],[10,2],[10.45,0],
                [18.75,0],[19.05,-3],[22.15,-3],[22.8,0],[26,0],[26.45,2],[29.45,2],[30.2,0],
                [34.9,0],[35.5,2],[38.05,2],[38.55,0],[39,-2],[43.9,-2],[44.6,-3],[47.1,-3],
                [47.5,0],[48,-3],[52.93,-3]],
   "reasons": ["Más presencia en apertura/bucle y entrada a aplicación.",
               "Retirar3dB al explicar entrada/criterios, donde18–22s da el menor E-STOI de C.",
               "Espacio para las reglas/sistema y pregunta final; no elevar en todos los huecos."],
   "fx_hook_start_s":.025, "hook_extra_db":2.5,
 },
 "largo-159": {
   "music_db": [[0,0],[.6,2.5],[2,2.5],[2.35,0],[5.6,-2],[13.2,-2],[13.75,2],[22.8,2],[23.6,0],
                [24,-2],[33.4,-2],[34,0],[37.5,2],[42.7,2],[43,0],[48.2,0],[48.7,-3],[61.55,-3],
                [62.15,0],[63.25,2.5],[67.8,2.5],[69.25,0],[83,0],[93.25,0],[93.95,1.5],
                [96.45,1.5],[96.9,-2],[107.4,-2],[115.6,0],[120.4,0],[120.85,-3],[125.5,-3],
                [126,-2],[132.4,-2],[133,0],[136,0],[136.65,2],[141.2,2],[142.05,0],[146,-3],[158.798,-3]],
   "reasons": ["Más presencia en apertura, volumen de contenido, datos/experiencia y entrada de acción.",
               "Bajar3dB en conversación/ventaja y no acumular otro curso; ventanas débiles58–62 y120–124s.",
               "Retirada para oferta/promesa, desorden, criterio y pregunta. Mantener silencio musical83–93s."],
   "fx_hook_start_s":.04, "hook_extra_db":2.5,
 },
}


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    originals = json.loads((BANK/"variantes-largas/manifest.json").read_text())
    result = []
    for piece, plan in PLANS.items():
        source = BANK/"variantes-largas"/piece/"C"
        folder = OUT/"comparaciones"/piece
        folder.mkdir(parents=True,exist_ok=True)
        voice_file = BANK/"renders/v2"/(piece+"-voz-sola.wav")
        voice, fs = sf.read(voice_file,dtype="float32",always_2d=True)
        music, fs2 = sf.read(source/"musica.wav",dtype="float32",always_2d=True)
        fx, fs3 = sf.read(source/"efectos.wav",dtype="float32",always_2d=True)
        assert fs == fs2 == fs3 == FS and voice.shape == music.shape == fx.shape
        t = np.arange(len(voice))/FS
        points = np.array(plan["music_db"])
        envelope = 10**(np.interp(t,points[:,0],points[:,1])/20)
        new_music = music*envelope[:,None]
        row = next(x for x in originals if x['id']==piece and x['variant']=='C')
        # Use the real hook binding from the existing plan, not a guessed timestamp.
        event = min(row['sfx_events'],key=lambda x:x['start'])
        a,b = round(event['start']*FS), round((event['start']+event['duration_s'])*FS)
        new_fx = fx.copy();new_fx[a:b] *= 10**(plan['hook_extra_db']/20)
        mix = voice+new_music+new_fx
        assert np.isfinite(mix).all() and abs(mix).max()<.89
        reconstructed = mix-new_music-new_fx
        voice_error = float(np.max(abs(reconstructed-voice)))
        assert voice_error < 2e-7
        for name,data in [('mezcla',mix),('musica',new_music),('efectos',new_fx)]:
            sf.write(folder/(name+'.wav'),data,FS,subtype="FLOAT")
        output = folder/'mezcla.m4a'
        subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-y','-i',str(folder/'mezcla.wav'),
                        '-c:a','aac','-b:a','256k','-ar',str(FS),str(output)],check=True)
        command = [FFMPEG,'-hide_banner','-i',str(output),'-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-']
        meter=subprocess.run(command,capture_output=True,text=True,check=True).stderr
        (folder/'loudness.log').write_text(meter)
        loudness=json.loads(meter[meter.rfind('{'):meter.rfind('}')+1])
        assert float(loudness['input_tp']) < -1.5
        ref16=signal.resample_poly(voice.mean(axis=1),1,3)
        decoded=read_audio(output)[:len(voice)]
        mix16=signal.resample_poly(decoded,1,3)
        n=min(len(ref16),len(mix16));scores=indices(ref16[:n],mix16[:n])
        original_scores=next(x for x in json.loads((OUT/'evidencia/indices.json').read_text())['items'] if x['id']==piece+'-C')['whole']
        assert scores['estoi']>=original_scores['estoi']-.015
        windows=[]
        for start in np.arange(0,len(voice)/FS-3.99,2):
            a,b=round(start*16000),round((start+4)*16000)
            windows.append({'start_s':float(start),'end_s':float(start+4),**indices(ref16[a:b],mix16[a:b])})
        row={'piece':piece,'status':'CANDIDATA_PARA_COMPARAR','based_on':'C','plan':plan,
             'manual_editorial_hypothesis':True,'human_listening':False,'no_automatic_perceptual_approval':True,
             'input_voice_sha256':hash_file(voice_file),'input_music_sha256':hash_file(source/'musica.wav'),
             'input_sfx_sha256':hash_file(source/'efectos.wav'),'voice_reconstruction_max_error':voice_error,
             'hook_binding':event,'loudness_aac':loudness,'whole':scores,'source_C_whole':original_scores,
             'windows':windows,'files':{str(p.relative_to(OUT)):{'sha256':hash_file(p),'bytes':p.stat().st_size}
                                    for p in folder.glob('*') if p.suffix in ['.wav','.m4a']}}
        result.append(row);print(piece,'nativeAAC',loudness['input_i'],loudness['input_tp'],'ESTOI',scores['estoi'],flush=True)
    (OUT/'comparaciones/manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    main()
