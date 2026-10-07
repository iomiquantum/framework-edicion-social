"""Real-media acceptance checks for the reusable CLI, not browser automation."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

from evaluar_indices import OUT, ROOT, BANK

CLI=ROOT/'Framework-Edicion-Social/scripts/audio_multimedia'
DEST=OUT/'headless/v2'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    DEST.mkdir(parents=True,exist_ok=True)
    rows=[]
    def call(name,args,success=True,expected=None):
        started=time.monotonic();command=[str(CLI)]+list(map(str,args))
        result=subprocess.run(command,capture_output=True,text=True)
        record={'id':name,'command':command,'elapsed_process_seconds':time.monotonic()-started,
                'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'opens_interface':False}
        if success:assert result.returncode==0,record
        else:assert result.returncode!=0 and expected in result.stderr,record
        if result.stdout:
            record['result']=json.loads(result.stdout)
        rows.append(record)
        (DEST/'aceptacion.json').write_text(json.dumps({'all_checks_passed_so_far':True,'cases':rows},ensure_ascii=False,indent=2)+'\n')
        print(name,result.returncode,round(record['elapsed_process_seconds'],3),record.get('result',{}).get('cached') if isinstance(record.get('result',{}),dict) else '',flush=True)
        return record
    call('doctor',['doctor'])
    call('catalogo',['catalog','--type','music','--role','impulso'])
    plan=OUT/'headless/plan-piloto-01.json';pilot=DEST/'piloto-01'
    call('mezclar_y_revisar',['mix','--plan',plan,'--out',pilot,'--review'])
    row=call('mix_y_review_reutilizados',['mix','--plan',plan,'--out',pilot,'--review'])
    assert row['result']['cached'] and row['result']['review']['cached']
    # Real timed words and existing phrase boundaries; no transcription repeated.
    original=ROOT/'Serie-IA-Negocios-10-Videos/VIDEO-01/editable-hyperframes-video-01/transcript-final.json'
    phrases=json.loads((BANK/'evidencia/prosodia-01.json').read_text())['phrases']
    direction=DEST/'direction-01.json'
    direction.write_text(json.dumps({'sections':[{'start_s':r['start_s'],'end_s':r['end_s'],'text':r['text']} for r in phrases]},ensure_ascii=False,indent=2)+'\n')
    pro=['prosody','--voice',BANK/'renders/v2/01-voz-sola.wav','--transcript',original,'--direction',direction,'--out',DEST/'prosody-01']
    first=call('prosodia_primera',pro);again=call('prosodia_cache',pro)
    assert not first['result']['cached'] and again['result']['cached']
    for piece in ['largo-53','largo-159']:
        files=OUT/'comparaciones'/piece
        args=['review','--voice',BANK/'renders/v2'/(piece+'-voz-sola.wav'),'--mix',files/'mezcla.m4a',
              '--music',files/'musica.wav','--sfx',files/'efectos.wav','--out',DEST/(piece+'-review')]
        a=call(piece+'_review',args);b=call(piece+'_cache',args)
        assert not a['result']['cached'] and b['result']['cached']
    base=json.loads(plan.read_text())
    guard_dir=DEST/'guards';guard_dir.mkdir(exist_ok=True)
    def guard(name,change,message):
        cfg=json.loads(json.dumps(base));change(cfg)
        path=guard_dir/(name+'.json');path.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n')
        return call(name,['mix','--plan',path,'--out',guard_dir/(name+'-output')],False,message)
    guard('fuente_alterada',lambda c:c['voice'].update(sha256='0'*64),'Source hash missing or mismatched')
    guard('hook_ausente',lambda c:c['sfx'][0].update(hook=False),'Hook must contain')
    guard('identidades_repetidas',lambda c:c['sfx'].__setitem__(1,{**c['sfx'][0],'start_s':11.7,'hook':False}),'at least two real SFX identities')
    guard('evento_fuera',lambda c:c['sfx'][1].update(start_s=21.3),'Clip is outside voice timeline')
    guard('parametro_desconocido',lambda c:c['music'][0].update(gay_db=-18),'Unsupported clip options')
    reject=ROOT/'Framework-Edicion-Social/library/sfx/candidates/motion_fabric_swish_soft_v01.wav'
    guard('sfx_rechazado',lambda c:c['sfx'][0].update(file=str(reject),sha256=digest(reject)),'Explicitly rejected SFX')
    before={p.name:digest(p) for p in pilot.glob('*') if p.is_file()}
    changed=json.loads(json.dumps(base));changed['music'][0]['gain_db_points'][1][1]+=.1
    changed_file=guard_dir/'otra-version.json';changed_file.write_text(json.dumps(changed,ensure_ascii=False,indent=2)+'\n')
    call('preservar_version',['mix','--plan',changed_file,'--out',pilot],False,'Output has a different version')
    assert before=={p.name:digest(p) for p in pilot.glob('*') if p.is_file()}
    receipt={'status':'PASS','cases':rows,'previous_output_unchanged':True,'all_via_code':True,
             'timing_scope':'One execution per condition on this Mac. Includes interpreter startup; no general production speed claim.',
             'mix_first_run_seconds_from_receipt':json.loads((pilot/'mix.json').read_text())['elapsed_seconds'],
             'human_listening':False}
    (DEST/'aceptacion.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
