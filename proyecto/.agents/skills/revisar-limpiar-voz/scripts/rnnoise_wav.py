"""Process one native 48 kHz context with a pinned RNNoise library into a NEW WAV.

Explicit-only skill helper. No discovery, download, normalization, mixing or edit.
Delay is a measured caller input; this helper does not determine voice fidelity.
"""
from pathlib import Path
import argparse, ctypes as C, hashlib, json, time
import numpy as np
import soundfile as sf

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--library',type=Path,required=True)
    ap.add_argument('--expected-library-sha256',required=True)
    ap.add_argument('--delay-samples',type=int,required=True)
    ap.add_argument('--receipt',type=Path)
    args=ap.parse_args()
    src=args.input.resolve();out=args.output.resolve();lib=args.library.resolve()
    receipt=(args.receipt or out.with_suffix('.receipt.json')).resolve()
    if out==receipt or out in [src,lib] or receipt in [src,lib]:ap.error('Input, output, library and receipt paths must be distinct.')
    if out.exists() or receipt.exists():ap.error('Output and receipt must be new files; existing artifacts are preserved.')
    if not 0<=args.delay_samples<=4800:ap.error('Supply measured delay between 0 and 4800 samples.')
    libsha=sha(lib)
    if libsha!=args.expected_library_sha256.lower():ap.error('Library SHA256 mismatch; no code loaded.')
    original_sha=sha(src)
    x,sr=sf.read(src,dtype='float32',always_2d=True)
    if sr!=48000 or x.shape[1] not in [1,2] or len(x)<480:ap.error('Input must be mono/stereo 48 kHz, at least 10 ms.')
    if not np.isfinite(x).all():ap.error('Non-finite input samples.')
    mono=x.mean(axis=1);frames=(len(mono)+4800+479)//480
    padded=np.pad(mono,(0,frames*480-len(mono)));y=np.empty_like(padded)
    dll=C.CDLL(str(lib))
    dll.rnnoise_create.argtypes=[C.c_void_p];dll.rnnoise_create.restype=C.c_void_p
    dll.rnnoise_process_frame.argtypes=[C.c_void_p,C.POINTER(C.c_float),C.POINTER(C.c_float)];dll.rnnoise_process_frame.restype=C.c_float
    dll.rnnoise_destroy.argtypes=[C.c_void_p]
    state=dll.rnnoise_create(None)
    if not state:raise RuntimeError('RNNoise allocation failed')
    t=time.monotonic()
    try:
        for start in range(0,len(padded),480):
            inp=np.ascontiguousarray(padded[start:start+480]*32768,dtype=np.float32);buf=np.empty(480,dtype=np.float32)
            dll.rnnoise_process_frame(state,buf.ctypes.data_as(C.POINTER(C.c_float)),inp.ctypes.data_as(C.POINTER(C.c_float)))
            y[start:start+480]=buf/32768
    finally:dll.rnnoise_destroy(state)
    elapsed=time.monotonic()-t
    z=y[args.delay_samples:args.delay_samples+len(x)]
    if len(z)!=len(x) or not np.isfinite(z).all():raise RuntimeError('Invalid output samples')
    out.parent.mkdir(parents=True,exist_ok=True);receipt.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive creation preserves artifacts even if another task races this call.
    with out.open('xb') as f:sf.write(f,np.repeat(z[:,None],2,axis=1),48000,format='WAV',subtype='FLOAT')
    info=sf.info(out)
    if info.frames!=len(x) or info.samplerate!=48000 or info.channels!=2:raise RuntimeError('Output metadata mismatch')
    if sha(src)!=original_sha:raise RuntimeError('Source changed during processing')
    record=dict(input=str(src),input_sha256=original_sha,input_channels=x.shape[1],output=str(out),output_sha256=sha(out),library=str(lib),library_sha256=libsha,sample_rate=48000,samples=len(x),duration_s=len(x)/48000,frame_samples=480,input_float_scale=32768,compensated_delay_samples=args.delay_samples,padding_samples=len(padded)-len(x),channels='Explicit (L+R)/2 for stereo, mono duplicated to L/R',inference_s=elapsed,normalization='none',human_listened=False,approved=False)
    with receipt.open('x') as f:json.dump(record,f,indent=2);f.write('\n')
    print(json.dumps(record))

if __name__=='__main__':main()
