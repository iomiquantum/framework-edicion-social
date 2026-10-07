#!/usr/bin/env python3
"""Headless native audio mixing and bounded perceptual evidence. No human-hearing claims."""
import os
import argparse
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

import numpy as np
from scipy import ndimage, signal
import soundfile as sf
from pystoi import stoi

FW = Path(__file__).resolve().parents[1]
SR = 48000
MODEL = Path(os.environ.get('AUDIO_MULTIMEDIA_MODELS', str(Path(__file__).resolve().parents[3]/'runtime/models/yamnet')))
CAL = FW/'research/escucha-perceptual-2026-10-01/calibracion'
FF = os.environ.get('HYPERFRAMES_FFMPEG_PATH') or shutil.which('ffmpeg') or ''
if not Path(FF).exists():
    FF = shutil.which('ffmpeg')
PROBE = str(Path(FF).with_name('ffprobe.exe' if __import__('os').name == 'nt' else 'ffprobe')) if FF else None


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def save(path,data):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def execute(cmd):
    return subprocess.run(cmd,capture_output=True,check=True)


def media(path):
    probe=json.loads(execute([PROBE,'-v','error','-select_streams','a:0','-show_streams','-of','json',str(path)]).stdout)
    stream=probe['streams'][0];channels=stream['channels']
    if channels not in (1,2):raise ValueError('Only explicit mono or stereo sources supported')
    raw=execute([FF,'-v','error','-i',str(path),'-map','0:a:0','-ar',str(SR),'-f','f32le','-']).stdout
    data=np.frombuffer(raw,dtype='<f4').reshape(-1,channels).copy()
    if channels==1:data=np.repeat(data,2,axis=1) # unity duplication, no implicit -3dB negotiation
    if not np.isfinite(data).all() or len(data)==0:raise ValueError('Non-finite or empty source')
    return data,stream


def rms(x):return float(np.sqrt(np.mean(np.square(x,dtype=np.float64))))
def db(x):return float(20*np.log10(max(float(x),1e-12)))
def filt(x,lo,hi):return signal.sosfilt(signal.butter(3,[lo,hi],btype='bandpass',fs=SR,output='sos'),x,axis=0)


def frames(x,hop=.05):
    n=round(hop*SR);x=np.pad(x,((0,(-len(x))%n),(0,0)))
    return np.sqrt(np.mean(np.square(x.reshape(-1,n,2),dtype=np.float64),axis=(1,2)))


def expand(x,n):return np.interp(np.arange(n)/SR,(np.arange(len(x))+.5)*.05,x)


def curve(points,t):
    p=np.asarray(points,dtype=float)
    if p.ndim!=2 or p.shape[1]!=2 or not np.isfinite(p).all() or np.any(np.diff(p[:,0])<=0):
        raise ValueError('Gain points require unique increasing seconds and finite dB')
    if abs(p[:,1]).max()>80:raise ValueError('Gain outside supported +-80dB range')
    return 10**(np.interp(t,p[:,0],p[:,1])/20)


def version():
    return {p:importlib.metadata.version(p) for p in ['numpy','scipy','soundfile','pystoi','ai-edge-litert']}


def ffmpeg_version():
    return execute([FF,'-version']).stdout.decode().splitlines()[0]


def sfx_catalog():
    base=FW/'library/sfx';result=[]
    reviewed=json.loads((base/'candidates/review.json').read_text())
    soft_ids={'entry_velvet_bloom_soft_v01.wav':'SFX-ENTRY-0002','entry_warm_breath_lift_soft_v01.wav':'SFX-ENTRY-0003',
              'motion_fabric_swish_soft_v01.wav':'SFX-MOTION-0002','motion_warm_slide_soft_v01.wav':'SFX-MOTION-0003'}
    for manifest,group in [(base/'manifest.json','original'),(base/'candidates/manifest.json','soft'),
                           (base/'candidates/2026-09-30-musicalizacion/manifest.json','research')]:
        data=json.loads(manifest.read_text())
        for r in data.get('files',data.get('sfx',[])):
            if group=='research':path=FW.parent/r['file'];id=r['id'];status='candidate_not_globally_approved'
            else:
                path=base/r['file'];id=soft_ids.get(path.name,'SFX-ORIGINAL-'+path.name[:2])
                status='context_review_pending'
                if id in reviewed['approved']:status='approved_for_reuse'
                if id in reviewed['rejected'] or path.name in ['01_airy_in.wav','02_soft_whoosh.wav']:status='rejected_do_not_reuse'
            result.append({'id':id,'type':'sfx','file':str(path.resolve()),'sha256':sha(path),
                           'status':status,'role':r.get('role',r.get('purpose',r.get('description',''))),
                           'duration_s':r.get('duration_s',r.get('duration_seconds')),'license':r['license'],
                           'credit':r.get('source',r.get('provenance')),'source_manifest':str(manifest)})
    return result


def stamp():
    return {'script_sha256':sha(__file__),'packages':version(),'ffmpeg':ffmpeg_version(),'yamnet_sha256':sha(MODEL/'model.tflite'),
            'yamnet_labels_sha256':sha(MODEL/'yamnet_class_map.csv'),
            'calibration_hashes':{p.name:sha(p) for p in [CAL/'validacion-indices.json',CAL/'validacion-yamnet.json']}}


def check_calibration():
    a=json.loads((CAL/'validacion-indices.json').read_text());b=json.loads((CAL/'validacion-yamnet.json').read_text())
    if not a['speech_music_scope_pass'] or not b['pass']:raise ValueError('Required bounded calibration has not passed')
    if sha(MODEL/'model.tflite')!='4d8b4a53282dc83ef04e3e7dbc4fbc98082e34e44ed798e16c3a0cdd4c584faf':
        raise ValueError('Classifier differs from calibrated model')
    # Results do not validate arbitrary new library versions.
    expected={'numpy':'2.4.6','scipy':'1.17.1','pystoi':'0.4.1','ai-edge-litert':'2.2.0'}
    if any(importlib.metadata.version(k)!=v for k,v in expected.items()):
        raise ValueError('Runtime changed; recalibrate or use the recorded isolated runtime')


def classify(x,out):
    from ai_edge_litert.interpreter import Interpreter
    names=[r['display_name'] for r in csv.DictReader((MODEL/'yamnet_class_map.csv').open())]
    model=Interpreter(model_path=str(MODEL/'model.tflite'),num_threads=2);model.allocate_tensors()
    i=model.get_input_details()[0]['index'];o=model.get_output_details()[0]['index']
    scores=[];clock=[]
    for start in range(0,len(x),7680):
        z=x[start:start+15600].astype(np.float32);z=np.pad(z,(0,15600-len(z)))
        model.set_tensor(i,z);model.invoke();scores.append(model.get_tensor(o)[0]);clock.append(start/16000)
    matrix=np.asarray(scores);assert np.isfinite(matrix).all()
    np.savez_compressed(out/'yamnet.npz',scores=matrix,time_s=np.array(clock))
    return {'frame_count':len(matrix),'window_s':.975,'hop_s':.48,'end_padded':True,
            'headline':{name:float(matrix[:,names.index(name)].mean()) for name in ['Speech','Music','Silence']},
            'interpretation':'Activations, not human probabilities, gain recommendations or SFX audibility.'}


def meter(path):
    log=execute([FF,'-hide_banner','-nostats','-i',str(path),'-af',
                 'loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr.decode()
    data=json.loads(log[log.rfind('{'):log.rfind('}')+1])
    return {k:float(data[k]) for k in ['input_i','input_tp','input_lra']}


def review(args):
    started=time.monotonic();check_calibration()
    inputs={k:Path(v).resolve() for k,v in [('voice',args.voice),('mix',args.mix),('music',args.music),('sfx',args.sfx)] if v}
    identity={'inputs':{k:{'path':str(p),'sha256':sha(p)} for k,p in inputs.items()},
              'window_s':args.window,'hop_s':args.hop,'version':stamp()}
    signature=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    run_dir=Path(args.out).resolve()/signature[:16];file=run_dir/'report.json'
    if file.exists():
        report=json.loads(file.read_text())
        seal=json.loads((run_dir/'seal.json').read_text())
        if seal['report_sha256']==sha(file) and report['signature']==signature and all(sha(run_dir/f)==h for f,h in report['evidence_hashes'].items()):
            return {'cached':True,'report':str(file),'signature':signature,'elapsed_seconds':time.monotonic()-started}
        raise ValueError('Cached evidence changed; use a new output location and investigate')
    if not .5<=args.window<=30 or not .1<=args.hop<=args.window:raise ValueError('Invalid window/hop')
    run_dir.mkdir(parents=True,exist_ok=True)
    voice,_=media(inputs['voice']);mix,stream=media(inputs['mix']);extra=len(mix)-len(voice)
    if abs(extra)>.05*SR:raise ValueError('Unaligned duration: voice and mix require the same timeline')
    n=min(len(voice),len(mix));voice=voice[:n];mix=mix[:n]
    if rms(voice)<1e-7:raise ValueError('Voice control is empty/silent')
    reference=signal.resample_poly(voice.mean(axis=1),1,3)
    observed=signal.resample_poly(mix.mean(axis=1),1,3)
    windows=[]
    for start in np.arange(0,n/SR-args.window+.00001,args.hop):
        a,b=round(start*16000),round((start+args.window)*16000)
        # Short inactive windows are retained but not treated as speech clarity verdicts.
        windows.append({'start_s':float(start),'end_s':float(start+args.window),
                        'estoi':float(stoi(reference[a:b],observed[a:b],16000,extended=True))})
    report={**identity,'signature':signature,'human_listener':False,'duration_s':n/SR,'codec':stream['codec_name'],
            'source_sample_rate':stream['sample_rate'],'source_channels':stream['channels'],'aac_or_container_extra_samples':extra,
            'stoi':float(stoi(reference,observed,16000)),'estoi':float(stoi(reference,observed,16000,extended=True)),
            'windows':windows,'review_candidates':sorted(windows,key=lambda v:v['estoi'])[:5],
            'loudness':meter(inputs['mix']),'mono_rms_change_db':db(rms(mix.mean(axis=1))/max(rms(mix),1e-12)),
            'yamnet':classify(observed.astype(np.float32),run_dir),
            'status':'EVALUACION_ASISTIDA_PARCIAL',
            'excluded':['Human emotional/creative fit','SFX audibility','Audience attention','Automatic fader choice'],
            'decisions_required':'Read the phrase at each candidate window. A low estimate does not mandate a volume reduction.'}
    if 'music' in inputs and 'sfx' in inputs:
        music,_=media(inputs['music']);sfx,_=media(inputs['sfx'])
        if abs(len(music)-n)>.05*SR or abs(len(sfx)-n)>.05*SR:raise ValueError('Stems do not align')
        native_mix=None
        if inputs['mix'].suffix.lower()=='.wav':native_mix=mix
        if native_mix is not None:
            error=float(abs(native_mix-(voice+music[:n]+sfx[:n])).max())
            report['stems_sum_max_error']=error
            if error>1e-6:raise ValueError('Written PCM voice contribution differs from control')
        else:
            expected=voice+music[:n]+sfx[:n]
            report['aac_stems_correlation']=float(np.corrcoef(expected.reshape(-1),mix.reshape(-1))[0,1])
            if report['aac_stems_correlation']<.999:raise ValueError('Codec differs from expected stem sum')
        band_voice=frames(filt(voice,350,5000));active=frames(voice)>np.percentile(frames(voice),95)*10**(-22/20)
        bands={}
        for role,x in [('music',music[:n]),('sfx',sfx[:n])]:
            level=frames(filt(x,350,5000));valid=active&(band_voice>1e-7)&(level>1e-7)
            ratio=20*np.log10(np.maximum(level,1e-12)/np.maximum(band_voice,1e-12))
            bands[role]={'active_frames':int(valid.sum()),'relative_db_p50':float(np.median(ratio[valid])) if valid.any() else None,
                         'relative_db_p95':float(np.percentile(ratio[valid],95)) if valid.any() else None,
                         'frames_above_voice':int((valid&(ratio>0)).sum()),'scope':'Acoustic diagnostic only, not validated human masking.'}
        report['speech_band_relationships']=bands
    report['elapsed_seconds']=time.monotonic()-started
    report['evidence_hashes']={'yamnet.npz':sha(run_dir/'yamnet.npz')}
    save(file,report);save(run_dir/'seal.json',{'report_sha256':sha(file),'signature':signature})
    save(Path(args.out)/'latest.json',{'report':str(file),'signature':signature})
    return {'cached':False,'report':str(file),'signature':signature,'elapsed_seconds':time.monotonic()-started}


def mix_plan(args):
    started=time.monotonic();plan_file=Path(args.plan).resolve();plan=json.loads(plan_file.read_text())
    if plan.get('schema')!='audio-multimedia/v1':raise ValueError('Expected schema audio-multimedia/v1')
    allowed={'schema','id','voice','music','sfx','music_bus','hook_window_s','notes'}
    if set(plan)-allowed:raise ValueError('Unsupported plan options: '+str(set(plan)-allowed))
    if set(plan['voice'])-{'file','sha256','gain_db'}:raise ValueError('Unsupported voice parameters; specialized restoration is a separate workflow')
    clip_options={'file','sha256','credit','license','reason','start_s','duration_s','source_start_s','level_mode',
                  'gain_db','gain_db_points','pan','width','fade_in_s','fade_out_s','reverse','tail_protect_fraction','hook'}
    base=plan_file.parent;bindings=[];cache={}
    rejected={r['sha256'] for r in sfx_catalog() if r['status']=='rejected_do_not_reuse'}
    def bind(item):
        p=Path(item['file']);p=p if p.is_absolute() else (base/p).resolve()
        digest=sha(p)
        if item.get('sha256')!=digest:raise ValueError('Source hash missing or mismatched: '+str(p))
        if digest in rejected:raise ValueError('Explicitly rejected SFX must not be reused: '+str(p))
        bindings.append({'path':str(p),'sha256':digest})
        return p
    voice_path=bind(plan['voice'])
    for item in plan.get('music',[])+plan.get('sfx',[]):
        if set(item)-clip_options:raise ValueError('Unsupported clip options: '+str(set(item)-clip_options))
        if not item.get('reason'):raise ValueError('Each music/SFX clip needs a contextual reason')
        if not item.get('credit') or not item.get('license'):raise ValueError('Missing music/SFX provenance')
        bind(item)
    signature=hashlib.sha256(json.dumps({'plan_sha256':sha(plan_file),'sources':bindings,'script_sha256':sha(__file__),
                                       'packages':version(),'ffmpeg':ffmpeg_version(),
                                       'sfx_review_sha256':sha(FW/'library/sfx/candidates/review.json')},sort_keys=True).encode()).hexdigest()
    out=Path(args.out).resolve();receipt=out/'mix.json'
    if receipt.exists():
        old=json.loads(receipt.read_text())
        if old['signature']==signature and all(sha(out/f)==h for f,h in old['files'].items()):
            result={'cached':True,'manifest':str(receipt),'elapsed_seconds':time.monotonic()-started}
            if args.review:result['review']=review_mix(out)
            return result
        raise ValueError('Output has a different version. Choose another --out; previous media are preserved.')
    if out.exists() and any(out.iterdir()):raise ValueError('Output folder must be new/empty')
    out.mkdir(parents=True,exist_ok=True)
    voice,voice_stream=media(voice_path)
    if int(voice_stream['sample_rate'])==16000:raise ValueError('Do not mix an ASR16k derivative. Use the native voice source.')
    voice=voice.astype(np.float64)*10**(float(plan['voice'].get('gain_db',0))/20);n=len(voice)
    if rms(voice)<1e-7:raise ValueError('No usable voice')
    vr=frames(voice);active=vr>np.percentile(vr,95)*10**(-22/20);ref=float(np.median(vr[active]))
    activity=expand(ndimage.gaussian_filter1d(active.astype(float),1.5),n)
    music=np.zeros_like(voice);sfx=np.zeros_like(voice);events=[]
    def clip(item,kind):
        p=Path(item['file']);p=p if p.is_absolute() else (base/p).resolve()
        if str(p) not in cache:cache[str(p)]=media(p)[0]
        a=round(float(item['start_s'])*SR);offset=round(float(item.get('source_start_s',0))*SR)
        length=round(float(item['duration_s'])*SR) if 'duration_s' in item else len(cache[str(p)])-offset
        if a<0 or offset<0 or length<=0 or a+length>n:raise ValueError('Clip is outside voice timeline')
        x=cache[str(p)][offset:offset+length].astype(np.float64).copy()
        if len(x)!=length:raise ValueError('Source excerpt is too short; choose another excerpt, no implicit loops')
        if item.get('reverse',False):x=x[::-1].copy()
        if item.get('level_mode','source')=='voice_relative':
            nearby=voice[max(0,a-round(.35*SR)):min(n,a+length+round(.25*SR))]
            anchor=ref if kind=='music' else min(ref*1.15,max(ref*.60,rms(nearby)))
            x*=anchor/max(rms(x),1e-12)
        elif item.get('level_mode','source')!='source':raise ValueError('Unknown level mode')
        t=np.arange(length)/SR+float(item['start_s'])
        x*=curve(item.get('gain_db_points',[[0,float(item.get('gain_db',0))]]),t)[:,None]
        pan=float(item.get('pan',0));width=float(item.get('width',1))
        if not -1<=pan<=1 or not 0<=width<=2:raise ValueError('Invalid pan or stereo width')
        mid=x.mean(axis=1);side=(x[:,0]-x[:,1])*.5*width;x=np.stack([mid+side,mid-side],axis=1)
        x[:,0]*=1-max(0,pan);x[:,1]*=1+min(0,pan)
        for key,reverse in [('fade_in_s',False),('fade_out_s',True)]:
            count=round(float(item.get(key,.04 if kind=='music' else .005))*SR)
            if count<0 or count>length//2:raise ValueError('Invalid fade length')
            if count:
                env=np.sin(np.linspace(0,np.pi/2,count))**2
                if reverse:x[-count:]*=env[::-1,None]
                else:x[:count]*=env[:,None]
        if kind=='sfx':
            fraction=float(item.get('tail_protect_fraction',0))
            if not 0<=fraction<=1:raise ValueError('Invalid SFX tail protection')
            env=np.ones(length);attack=min(length,round(.065*SR))
            env[attack:]-=fraction*activity[a+attack:a+length]
            x*=ndimage.gaussian_filter1d(env,240)[:,None]
            if rms(x)<1e-8:raise ValueError('SFX event is silent; it cannot satisfy presence or identity guards')
            events.append({'start_s':a/SR,'duration_s':length/SR,'source_sha256':item['sha256'],
                           'reason':item['reason'],'hook':bool(item.get('hook',False)),
                           'rms_relative_voice_db':db(rms(x)/max(rms(voice[a:a+length]),1e-12)),
                           'peak_dbfs':db(abs(x).max()),'audibility':'por confirmar'})
        return a,x
    for item in plan.get('music',[]):
        a,x=clip(item,'music');music[a:a+len(x)]+=x
    for item in plan.get('sfx',[]):
        a,x=clip(item,'sfx');sfx[a:a+len(x)]+=x
    hook=plan.get('hook_window_s',[0,min(2,n/SR)])
    if len(hook)!=2 or not 0<=hook[0]<hook[1]<=n/SR:raise ValueError('Invalid hook window')
    if not any(e['hook'] and hook[0]<=e['start_s']<hook[1] and e['peak_dbfs']>-120 for e in events):
        raise ValueError('Hook must contain a linked non-silent SFX')
    if 20<=n/SR<=30 and len({e['source_sha256'] for e in events})<2:
        raise ValueError('20-30s videos need at least two real SFX identities')
    bus=plan.get('music_bus',{})
    allowed_bus={'highpass_hz','lowpass_hz','carve_fraction','carve_band_hz','duck_max_db','duck_lookahead_s','duck_release_s','speech_margin_db','cap_max_db'}
    if set(bus)-allowed_bus:raise ValueError('Unsupported music bus parameters')
    for key,kind in [('highpass_hz','highpass'),('lowpass_hz','lowpass')]:
        if key in bus:music=signal.sosfilt(signal.butter(2,float(bus[key]),btype=kind,fs=SR,output='sos'),music,axis=0)
    carve=float(bus.get('carve_fraction',0))
    if not 0<=carve<=.8:raise ValueError('Carve must be0-.8')
    if carve:
        lo,hi=bus.get('carve_band_hz',[400,4000]);music-=filt(music,lo,hi)*carve*activity[:,None]
    reduction=np.zeros(len(vr))
    max_duck=float(bus.get('duck_max_db',0))
    if not 0<=max_duck<=18:raise ValueError('Duck maximum must be0-18dB')
    if max_duck:
        soft=np.clip(20*np.log10(np.maximum(vr,1e-12)/max(ref,1e-12))+3,-max_duck,0);soft[~active]=0
        look=float(bus.get('duck_lookahead_s',.15));release=float(bus.get('duck_release_s',.35))
        if not 0<=look<=1 or not .05<=release<=3:raise ValueError('Invalid duck timing')
        soft=ndimage.minimum_filter1d(soft,max(1,round(look/.05)*2+1),mode='nearest')
        reduction+=ndimage.gaussian_filter1d(soft,max(.2,release/.05/2))
        music*=expand(10**(reduction/20),n)[:,None]
    if 'speech_margin_db' in bus:
        margin=float(bus['speech_margin_db']);limit=float(bus.get('cap_max_db',8))
        if not 0<=margin<=30 or not 0<=limit<=18:raise ValueError('Invalid speech band cap')
        ve=ndimage.uniform_filter1d(frames(filt(voice,350,5000))**2,5)
        me=ndimage.uniform_filter1d(frames(filt(music,350,5000))**2,5)
        if min(ve.min(),me.min())<-1e-12:raise ValueError('Substantial negative energy')
        v=np.sqrt(np.maximum(ve,0));m=np.sqrt(np.maximum(me,0))
        cap=np.clip(20*np.log10(np.maximum(v,1e-10)/np.maximum(m,1e-10))-margin,-limit,0);cap[~active]=0
        cap=ndimage.gaussian_filter1d(ndimage.minimum_filter1d(cap,5),1.8)
        music*=expand(10**(cap/20),n)[:,None];reduction+=cap
    output=voice+music+sfx
    if not np.isfinite(output).all() or abs(output).max()>=1:raise ValueError('Non-finite/clipping mix: lower accompaniment in a new plan')
    for name,x in [('mezcla',output),('voz',voice),('musica',music),('efectos',sfx)]:sf.write(out/(name+'.wav'),x,SR,subtype='FLOAT')
    execute([FF,'-v','error','-i',str(out/'mezcla.wav'),'-c:a','aac','-b:a','256k','-movflags','+faststart',str(out/'mezcla.m4a')])
    measure=meter(out/'mezcla.m4a');decoded,_=media(out/'mezcla.m4a');corr=float(np.corrcoef(output.reshape(-1),decoded[:n].reshape(-1))[0,1])
    sum_error=float(abs(sf.read(out/'mezcla.wav',always_2d=True)[0]-sum(sf.read(out/(q+'.wav'),always_2d=True)[0] for q in ['voz','musica','efectos'])).max())
    if measure['input_tp']>-1.5 or corr<.999 or sum_error>1e-6:
        save(out/'failure.json',{'loudness':measure,'correlation':corr,'stems_error':sum_error,'decision':'Keep failed output and use another plan/output version.'})
        raise ValueError('Exact export QA failed; preserve attempt and adjust accompaniment')
    shutil.copy2(plan_file,out/'plan.json')
    save(out/'automation.json',{'secondary_reduction_db':reduction.tolist(),'hop_s':.05,'scope':'Downward-only accompaniment; manual music curves in plan.'})
    receipt_data={'signature':signature,'id':plan['id'],'sources':bindings,'status':'MEZCLA_TECNICA_CANDIDATA',
                  'voice_constant_gain_db':plan['voice'].get('gain_db',0),'voice_cleanup':False,'human_listener':False,
                  'loudness_aac':measure,'aac_pcm_correlation':corr,'written_stem_error':sum_error,'events':events,
                  'music_bus':bus,'elapsed_seconds':time.monotonic()-started,
                  'files':{p.name:sha(p) for p in out.iterdir() if p.suffix in ['.wav','.m4a','.json']}}
    save(receipt,receipt_data)
    result={'cached':False,'manifest':str(receipt),'elapsed_seconds':time.monotonic()-started}
    if args.review:
        result['review']=review_mix(out)
    return result


def review_mix(out):
    return review(argparse.Namespace(voice=str(out/'voz.wav'),mix=str(out/'mezcla.m4a'),music=str(out/'musica.wav'),
                                    sfx=str(out/'efectos.wav'),out=str(out/'review'),window=4,hop=2))


def catalog(args):
    if args.type=='music':
        data=json.loads((FW/'library/music/catalogo-editorial.json').read_text())['tracks']
        return [r for r in data if r['type']=='bgm' and (args.include_history or not r.get('history',False))
                and (not args.role or args.role in r.get('roles',[]))]
    return [r for r in sfx_catalog() if (args.include_history or r['status']!='rejected_do_not_reuse')
            and (not args.approved_only or r['status']=='approved_for_reuse')]


def prosody(args):
    files={k:Path(getattr(args,k)).resolve() for k in ['voice','transcript','direction']}
    sig=hashlib.sha256(json.dumps({k:sha(p) for k,p in files.items()},sort_keys=True).encode()+ffmpeg_version().encode()+
                       sha(FW/'scripts/perfilar_voz.py').encode()).hexdigest()
    out=Path(args.out).resolve()/sig[:16];out.mkdir(parents=True,exist_ok=True);report=out/'prosody.json'
    if report.exists():
        if json.loads((out/'seal.json').read_text())['report_sha256']!=sha(report):raise ValueError('Cached prosody changed')
        return {'cached':True,'report':str(report)}
    command=[sys.executable,str(FW/'scripts/perfilar_voz.py'),'--ffmpeg',FF,'--out',str(report)]
    for k,p in files.items():command+=['--'+k,str(p)]
    execute(command)
    save(out/'seal.json',{'report_sha256':sha(report),'signature':sig})
    return {'cached':False,'report':str(report),'signature':sig,'script':'Existing acoustic profiler; no new ASR.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);subs=parser.add_subparsers(dest='command',required=True)
    subs.add_parser('doctor',help='Check local runtime, calibrated model and capabilities')
    cat=subs.add_parser('catalog',help='Read existing local library, no download or adoption');cat.add_argument('--type',choices=['music','sfx'],default='music');cat.add_argument('--role')
    cat.add_argument('--approved-only',action='store_true',help='SFX with explicit reuse approval only')
    cat.add_argument('--include-history',action='store_true',help='Include rejected/history for inspection, never overrides mix guards')
    pro=subs.add_parser('prosody',help='Reuse timed transcript and acoustic profile by hash')
    for key in ['voice','transcript','direction','out']:pro.add_argument('--'+key,required=True)
    mixing=subs.add_parser('mix',help='Freeze a versioned JSON plan to48k stereo WAV/AAC/stems')
    mixing.add_argument('--plan',required=True);mixing.add_argument('--out',required=True);mixing.add_argument('--review',action='store_true')
    rev=subs.add_parser('review',help='Audio-input classification, intelligibility proxy and export measurements')
    for key in ['voice','mix','out']:rev.add_argument('--'+key,required=True)
    for key in ['music','sfx']:rev.add_argument('--'+key)
    rev.add_argument('--window',type=float,default=4);rev.add_argument('--hop',type=float,default=2)
    args=parser.parse_args()
    try:
        if args.command=='doctor':
            check_calibration();result={'python':sys.executable,'ffmpeg':FF,'versions':version(),'headless':True,
                'capabilities':{'mix':'native48k curves/fades/pan/width/EQ/carve/downward duck/SFX tail',
                'review':'ESTOI speech/music + YAMNet + acoustic bands/exact export/mono',
                'prosody':'Existing timing/F0/intensity/pause profile cached by source hash',
                'experimental_models':'Qwen/Gemma calibration retained; not routine gain or approval reviewers'},
                'human_hearing':False,'model_sha256':sha(MODEL/'model.tflite')}
        elif args.command=='catalog':result=catalog(args)
        elif args.command=='prosody':result=prosody(args)
        elif args.command=='mix':result=mix_plan(args)
        else:result=review(args)
        print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
    except Exception as error:
        print(json.dumps({'status':'ERROR','error':str(error)},ensure_ascii=False),file=sys.stderr);sys.exit(1)


if __name__=='__main__':main()
