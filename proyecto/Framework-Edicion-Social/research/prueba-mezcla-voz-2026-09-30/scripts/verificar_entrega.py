from pathlib import Path
import json,hashlib,subprocess,re
import numpy as np,soundfile as sf
from scipy import signal
OUT=Path(__file__).resolve().parents[1];ROOT=OUT.parents[2];FF='/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def db(x):return float(20*np.log10(max(x,1e-12)))
def measure(p):
 s=subprocess.run([FF,'-hide_banner','-nostats','-i',str(p),'-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
 m=json.loads(re.findall(r'\{\s*"input_i".*?\}',s,re.S)[-1]);return {k:float(m[k]) for k in ['input_i','input_tp','input_lra']}
manifest=json.loads((OUT/'manifest.json').read_text());records=[]
for m in manifest:
 assert sha(ROOT/m['source'])==m['source_sha256']
 media=[]
 for rel,rec in m['files'].items():
  p=OUT/rel;assert sha(p)==rec['sha256'];probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));s=probe['streams'][0];assert int(s['sample_rate'])==48000 and s['channels']==2
  subprocess.run([FF,'-v','error','-i',str(p),'-f','null','-'],check=True,capture_output=True)
  x=np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(p),'-f','f32le','-']),dtype='<f4');rms=float(np.sqrt(np.mean(x.astype(np.float64)**2)));assert np.isfinite(x).all() and rms>1e-6
  media.append({'file':rel,'sha256':rec['sha256'],'duration_s':float(probe['format']['duration']),'rms':rms,'peak_dbfs':db(float(abs(x).max())),'decode_full':'pass'})
 assert len({e['source_sha256'] for e in m['sfx_events']})>=2
 voice,sr=sf.read(OUT/f"renders/v2/{m['id']}-voz-sola.wav",always_2d=True,dtype='float32');fx,sr=sf.read(OUT/f"renders/v2/{m['id']}-efectos.wav",always_2d=True,dtype='float32');hook=np.sqrt(np.mean(fx[:round(2*sr)].astype(np.float64)**2));assert hook>1e-6
 measured=m['mix_loudness_aac'];assert measured['input_tp']<=-1.5
 events=[]
 for e in m['sfx_events']:
  p=ROOT/e['source'];assert sha(p)==e['source_sha256'];a=round(e['start']*sr);b=min(len(fx),a+round(e['duration_s']*sr));xx=fx[a:b];assert float(abs(xx).max())>1e-5
  events.append({'start_s':e['start'],'source_hash':e['source_sha256'],'rendered_peak_dbfs':db(float(abs(xx).max())),'rendered_rms':float(np.sqrt(np.mean(xx.astype(np.float64)**2)))})
 rel=json.loads((OUT/f"evidencia/relacion-{m['id']}.json").read_text());active=[q for q in rel if q['active'] and q['voice_band_dbfs']>-40 and q['music_v2_band_dbfs']>-65];ratios=np.array([q['music_v2_relative_band_db'] for q in active]);r1=np.array([q['music_v1_band_dbfs']-q['voice_band_dbfs'] for q in active]);
 # Band-relative flags over low-energy tails/pauses are reported separately, not labeled intelligibility failures.
 observed={'analysis_window_s':.05,'voice_band_floor_for_summary_dbfs':-40,'v1_relative_median_db':float(np.median(r1)),'v2_relative_median_db':float(np.median(ratios)),'v2_relative_p95_db':float(np.percentile(ratios,95)),'v2_relative_max_db':float(np.max(ratios)),'low_energy_ratios_excluded_from_summary':'Conservar curvas completas; residuos/pausas/colas no se interpretan como habla ni defecto.'}
 rec={'id':m['id'],'files':media,'sfx_hook_rms':float(hook),'events_verified_in_pcm':events,'aac_pcm_correlation':m['aac_pcm_correlation'],'voice_unchanged_except_constant_gain':m['voice_constant_gain_max_abs_error']<1e-6,'stems_sum_error':m['stems_sum_max_abs_error'],'music_vs_voice':observed,'technical_checks':'PASS','human_perception':'por confirmar'};records.append(rec);print(m['id'],'files',len(media),'band95',round(observed['v2_relative_p95_db'],1),flush=True)
result={'status':'PASS','pieces':len(records),'files_verified':sum(len(r['files']) for r in records),'records':records,'source_unchanged':True,'hook_and_two_sfx_identities':True,'true_peak_ceiling_aac_dbfs':-1.5,'intelligibility_and_timbre_not_certified':True,'human_review':'por confirmar'}
(OUT/'evidencia/validacion-entrega.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
