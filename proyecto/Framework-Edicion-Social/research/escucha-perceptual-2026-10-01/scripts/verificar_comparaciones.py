"""Audit the two written candidates, retained sources and real AAC exports."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import time

from ai_edge_litert.interpreter import Interpreter
import numpy as np
from scipy import signal
import soundfile as sf

from evaluar_indices import OUT, BANK, FS, FFMPEG
from clasificar_sonido import CACHE, HOP, WINDOW_SAMPLES


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rms(x):
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64))))


def main():
    started = time.monotonic()
    manifest = json.loads((OUT/'comparaciones/manifest.json').read_text())
    old_indices = json.loads((OUT/'evidencia/indices.json').read_text())
    source_audit = []
    for row in old_indices['items']:
        for role, entry in row['inputs'].items():
            path = Path(entry['path'])
            ok = sha(path) == entry['sha256']
            source_audit.append({'id':row['id'], 'role':role, 'path':str(path), 'sha256':entry['sha256'], 'unchanged':ok})
            assert ok, str(path)
    classifier = Interpreter(model_path=str(CACHE/'model.tflite'), num_threads=2)
    classifier.allocate_tensors()
    in_id = classifier.get_input_details()[0]['index']
    out_id = classifier.get_output_details()[0]['index']
    labels = [r['display_name'] for r in csv.DictReader((CACHE/'yamnet_class_map.csv').open())]
    result = []
    for row in manifest:
        piece = row['piece']; folder = OUT/'comparaciones'/piece
        voice_file = BANK/'renders/v2'/(piece+'-voz-sola.wav')
        voice, fs = sf.read(voice_file, dtype='float64', always_2d=True)
        arrays = {}
        for stem in ['mezcla','musica','efectos']:
            path = folder/(stem+'.wav')
            data, rate = sf.read(path, dtype='float64', always_2d=True)
            assert fs == rate == FS and data.shape == voice.shape
            assert np.isfinite(data).all() and rms(data)>0
            arrays[stem] = data
        voice_error = float(abs(arrays['mezcla']-arrays['musica']-arrays['efectos']-voice).max())
        assert voice_error < 2e-7
        audio_path = folder/'mezcla.m4a'
        probe = json.loads(subprocess.run([str(Path(FFMPEG).with_name('ffprobe')),'-v','error','-show_streams',
                          '-show_format','-of','json',str(audio_path)],capture_output=True,text=True,check=True).stdout)
        stream = probe['streams'][0]
        assert stream['codec_name']=='aac' and int(stream['sample_rate'])==FS and stream['channels']==2
        raw = subprocess.run([FFMPEG,'-v','error','-i',str(audio_path),'-f','f32le','-ar',str(FS),'-ac','2','-'],
                             capture_output=True,check=True).stdout
        decoded = np.frombuffer(raw,dtype='<f4').reshape(-1,2).astype(np.float64)
        extra = len(decoded)-len(voice)
        assert 0 <= extra < .05*FS
        decoded = decoded[:len(voice)]
        assert np.isfinite(decoded).all() and rms(decoded)>0
        corr = float(np.corrcoef(decoded.mean(axis=1),arrays['mezcla'].mean(axis=1))[0,1])
        assert corr > .999
        mono_change = 20*np.log10(rms(decoded.mean(axis=1))/rms(decoded))
        assert mono_change > -1, 'Potential new stereo cancellation'
        for rel, entry in row['files'].items():
            assert sha(OUT/rel)==entry['sha256']
        event = row['hook_binding']; a = round(event['start']*FS); b = round((event['start']+event['duration_s'])*FS)
        original_fx = sf.read(BANK/'variantes-largas'/piece/'C/efectos.wav',dtype='float64',always_2d=True)[0]
        hook_delta = 20*np.log10(rms(arrays['efectos'][a:b])/rms(original_fx[a:b]))
        assert abs(hook_delta-2.5)<.01 and rms(arrays['efectos'][a:b])>0
        # Native AAC input; only model derivative is downsampled to16k.
        audio16 = signal.resample_poly(decoded.mean(axis=1),1,3).astype(np.float32)
        frames=[]; clock=[]
        for start in range(0,len(audio16),HOP):
            block=audio16[start:start+WINDOW_SAMPLES]
            block=np.pad(block,(0,WINDOW_SAMPLES-len(block)))
            classifier.set_tensor(in_id,block)
            classifier.invoke()
            scores=classifier.get_tensor(out_id)[0]
            assert scores.shape==(521,) and np.isfinite(scores).all()
            frames.append(scores);clock.append(start/16000)
        matrix=np.asarray(frames)
        np.savez_compressed(OUT/'evidencia/yamnet-scores'/(piece+'-candidata.npz'),scores=matrix,time_s=np.array(clock))
        headline={name:float(matrix[:,labels.index(name)].mean()) for name in ['Speech','Music','Silence']}
        result.append({'piece':piece,'duration_pcm_s':len(voice)/FS,'probe':probe,
                       'voice_reconstruction_written_max_error':voice_error,'aac_pcm_mono_correlation':corr,
                       'aac_extra_samples':extra,'mono_rms_change_db':float(mono_change),
                       'hook_extra_written_db':float(hook_delta),'hook_audibility':'por confirmar',
                       'yamnet_frame_count':len(matrix),'yamnet_headline':headline,'human_listening':False})
        print(piece,'writtenVoiceError',voice_error,'AACcorr',corr,'monoDelta',mono_change,'CNN',headline,flush=True)
    receipt={'status':'LISTA_PARA_ESCUCHA_CON_EVALUACION_ASISTIDA_PARCIAL','source_audit':source_audit,
             'checks_pass':True,'results':result,'elapsed_seconds':time.monotonic()-started,
             'limitations':['No human perception or creative approval inferred.','YAMNet scores do not assess SFX audibility or prescribe gain.']}
    (OUT/'comparaciones/qa.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':
    main()
