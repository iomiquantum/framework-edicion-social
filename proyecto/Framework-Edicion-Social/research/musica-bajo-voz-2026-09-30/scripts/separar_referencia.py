"""Demucs local para estudiar una mezcla, sin recuperar sus pistas originales.

No normaliza stems independientemente; no son recursos musicales para reutilizar.
"""
import argparse
import hashlib
import json
import random
import time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from demucs.apply import apply_model
from demucs.pretrained import get_model

parser=argparse.ArgumentParser()
parser.add_argument('--ref',default='ref-01')
args=parser.parse_args()
OUT=Path(__file__).resolve().parents[1]/'referencias-usuario'/args.ref
MODEL=Path('/tmp/codex-referencia-mezcla-20260930/models/955717e8-8726e21a.th')
model_hash=hashlib.sha256(MODEL.read_bytes()).hexdigest()
assert model_hash.startswith('8726e21a'), 'Peso no coincide con checksum oficial'
torch.set_num_threads(4)
torch.manual_seed(0);np.random.seed(0);random.seed(0)
begin=time.monotonic()
wav,sr=sf.read(OUT/'mezcla.wav',dtype='float32',always_2d=True)
assert sr==44100 and wav.shape[1]==2
input_tensor=torch.from_numpy(wav.T.copy())
reference=input_tensor.mean(0)
mean,std=reference.mean(),reference.std()
normalized=(input_tensor-mean)/std
model=get_model('955717e8',repo=MODEL.parent).eval()
with torch.no_grad():
    sources=apply_model(model,normalized[None],device='cpu',shifts=0,split=True,
                        overlap=.25,segment=7,progress=True)[0]
sources=(sources*std+mean).cpu().numpy().transpose(0,2,1)
STEMS=OUT/'estimaciones-demucs';STEMS.mkdir(exist_ok=True)
records=[]
for name,x in zip(model.sources,sources):
    p=STEMS/(name+'.wav');sf.write(p,x,sr,subtype='FLOAT')
    records.append({'name':name,'path':str(p.relative_to(OUT)),
                    'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                    'peak_dbfs':float(20*np.log10(max(np.abs(x).max(),1e-12)))})
vocals=sources[model.sources.index('vocals')]
nonvoice=sum(x for name,x in zip(model.sources,sources) if name!='vocals')
sf.write(STEMS/'acompanamiento-estimado.wav',nonvoice,sr,subtype='FLOAT')
reconstruction=sources.sum(0)
result={'status':'completed_estimates_only','model':'htdemucs single955717e8',
        'demucs_version':'4.0.1','torch_version':torch.__version__,
        'model_sha256':model_hash,'model_url':'https://dl.fbaipublicfiles.com/demucs/hybrid_transformer/955717e8-8726e21a.th',
        'device':'cpu','threads':4,'seed':0,'shifts':0,'overlap':.25,'segment_s':7,
        'duration_s':len(wav)/sr,'sample_rate':sr,'normalization':'Una normalización de entrada revertida común; WAVFLOAT sin rescale/clamp por stem.',
        'reconstruction_correlation':float(np.corrcoef(reconstruction.ravel(),wav.ravel())[0,1]),
        'residual_rms_dbfs':float(20*np.log10(np.sqrt(np.mean((reconstruction-wav)**2)))),
        'elapsed_s':time.monotonic()-begin,'stems':records,
        'limits':['Modelo entrenado en música: vocals puede incluir habla y residuos; acompañamiento puede contener fuga de voz/SFX.',
                  'No son stems originales. No permite inferir faders/automatización exactos ni número de canciones.',
                  'Torch2.5.1 existente usado en entorno aislado; se evita sustituir por la antigua dependencia torchaudio<2.1 del paquete.',
                  'Fuentes originales intactas; derivados solo para análisis, no para biblioteca/reutilización de música.']}
(OUT/'separacion.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','elapsed_s','reconstruction_correlation','residual_rms_dbfs']},ensure_ascii=False))
