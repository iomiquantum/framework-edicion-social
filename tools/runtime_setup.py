"""Portable onboarding. Read-only detection; every installer needs a prepared consent plan."""
from __future__ import annotations
import ssl, urllib.error, gzip
import concurrent.futures, hashlib, json, os, platform, re, shutil, subprocess, sys, tarfile, tempfile, time, urllib.request, uuid, zipfile
from pathlib import Path
import windows
ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
 'node':'https://nodejs.org/dist/index.json',
 'hyperframes':'https://registry.npmjs.org/hyperframes/latest',
 'codex':'https://registry.npmjs.org/@openai%2fcodex/latest',
 'python':'https://www.python.org/downloads/',
 'ffmpeg':'https://ffmpeg.org/releases/',
 'audio':'https://pypi.org/pypi/ai-edge-litert/json',
}

def save(path, data): windows.save(path,data)
def read(path): return windows.read(path)
def now(): return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def request(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Edicion-Portable/2.0'})
    try:
        with urllib.request.urlopen(req,timeout=18) as response:
            raw=response.read();return gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
    except urllib.error.URLError as e:
        if not isinstance(e.reason,ssl.SSLCertVerificationError):raise
        # Python.org builds may lack their local CA bundle. Native curl still verifies TLS.
        curl='/usr/bin/curl' if sys.platform=='darwin' else shutil.which('curl.exe' if os.name=='nt' else 'curl')
        if not curl:raise
        result=subprocess.run([curl,'--fail','--silent','--show-error','--compressed','--location','--proto','=https','--proto-redir','=https','--max-time','30',url],capture_output=True,timeout=35)
        if result.returncode:raise RuntimeError(result.stderr.decode(errors='replace')[:500]) from e
        raw=result.stdout;return gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw
def json_url(url):return json.loads(request(url))
def run(args, timeout=45, env=None, cwd=None):
    result=subprocess.run([str(x) for x in args],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout,env=env,cwd=cwd)
    if result.returncode:raise RuntimeError((result.stderr or result.stdout)[-5000:] or f'Falló {args[0]}')
    return result.stdout.strip()
def version(text):
    m=re.search(r'(\d+)\.(\d+)(?:\.(\d+))?',text)
    return tuple(int(x or 0) for x in m.groups()) if m else (0,0,0)
def config():
    p=ROOT/'runtime.local.json'
    d=read(p) if p.exists() else {}
    # Absolute paths belong to one host; ignore them after a move or OS switch.
    return {k:v for k,v in d.items() if k not in ('node','ffmpeg','ffprobe','python','npm','audio_python') or isinstance(v,str) and Path(v).is_file()}
def binary(name):
    c=config()
    if c.get(name) and Path(c[name]).is_file():return c[name]
    suffix='.exe' if os.name=='nt' else ''
    if name in ('ffmpeg','ffprobe'):
        for base in ('/opt/homebrew/opt/ffmpeg-full/bin','/usr/local/opt/ffmpeg-full/bin'):
            if Path(base,name+suffix).is_file():return str(Path(base,name+suffix))
    search_path=os.environ.get('PATH','')
    if os.name=='nt':
        import winreg
        for hive,key in ((winreg.HKEY_CURRENT_USER,'Environment'),(winreg.HKEY_LOCAL_MACHINE,r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment')):
            try:
                with winreg.OpenKey(hive,key) as handle:
                    search_path+=os.pathsep+os.path.expandvars(winreg.QueryValueEx(handle,'Path')[0])
            except OSError:pass
    return shutil.which(name,path=search_path)
def local_python(group='audio'):
    return ROOT/'runtime'/group/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
def hf_command():
    c=config();v=c.get('hyperframes',read(ROOT/'kit-config.json')['hyperframes'])
    return windows.cli({'hyperframes':v},{'node':binary('node')}),v
def environment():
    env=dict(os.environ)
    paths=[str(Path(p).parent) for n in ('node','ffmpeg') if (p:=binary(n))]
    env.update(PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',HYPERFRAMES_NO_UPDATE_CHECK='1',HF_HUB_DISABLE_TELEMETRY='1',DO_NOT_TRACK='1')
    env['PATH']=os.pathsep.join(paths+[env.get('PATH','')])
    for name in ('ffmpeg','ffprobe'):
        if binary(name):env['HYPERFRAMES_'+name.upper()+'_PATH']=binary(name)
    env['AUDIO_MULTIMEDIA_MODELS']=str(ROOT/'runtime/models/yamnet')
    env['AUDIO_MULTIMEDIA_PYTHON']=str(local_python())
    return env

def latest():
    def one(key,url):
        try:
            if key=='node':
                rows=json_url(url);current=next(x for x in rows if re.fullmatch(r'v\d+\.\d+\.\d+',x['version']))
                lts=next(x for x in rows if x.get('lts'))
                return {'version':current['version'].lstrip('v'),'lts':lts['version'].lstrip('v')}
            if key in ('hyperframes','codex'):return {'version':json_url(url)['version']}
            if key=='python':
                vals=re.findall(r'Python (3\.\d+\.\d+)(?![\da-z])',request(url).decode())
                return {'version':max(vals,key=version)}
            if key=='ffmpeg':
                vals=re.findall(r'ffmpeg-(\d+\.\d+(?:\.\d+)?)\.tar',request(url).decode())
                return {'version':max(vals,key=version)}
            return {'version':json_url(url)['info']['version']}
        except Exception as e:return {'error':str(e)[:250],'version':None}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        tasks={k:pool.submit(one,k,u) for k,u in SOURCES.items()}
        result={k:{**v.result(),'source':SOURCES[k]} for k,v in tasks.items()}
    return {'checked_at':now(),'checked_epoch':time.time(),'releases':result,'policy':'Última estable consultada ahora. Versiones nuevas no equivalen a compatibilidad comprobada.'}

def hardware():
    info={'os':platform.platform(),'architecture':platform.machine(),'cpu':platform.processor() or 'por confirmar','ram_gb':None,'gpu':'por confirmar','free_gb':round(shutil.disk_usage(ROOT).free/1e9,1)}
    try:
        if sys.platform=='darwin':
            info['cpu']=run(['sysctl','-n','machdep.cpu.brand_string'])
            info['ram_gb']=round(int(run(['sysctl','-n','hw.memsize']))/2**30,1)
            data=json.loads(run(['system_profiler','SPDisplaysDataType','-json'],timeout=30))
            info['gpu']=', '.join(x.get('sppci_model','por confirmar') for x in data['SPDisplaysDataType'])
        elif os.name=='nt':
            # Fixed script, no user-controlled interpolation.
            command="$c=Get-CimInstance Win32_Processor; $m=Get-CimInstance Win32_ComputerSystem; $g=Get-CimInstance Win32_VideoController; @{cpu=($c.Name -join ', '); ram_gb=[math]::Round($m.TotalPhysicalMemory/1GB,1); gpu=($g.Name -join ', ')} | ConvertTo-Json -Compress"
            info.update(json.loads(run(['powershell.exe','-NoProfile','-Command',command])))
    except Exception as e:info['detail']=str(e)[:240]
    if sys.platform=='darwin':info['profile']='mac-auto'
    else:info['profile']='pc-a-gtx1660ti' if '1660' in info['gpu'] else 'pc-b-uhd620'
    info['advice']='Un trabajo pesado a la vez. La RAM y las pruebas reales mandan; no se reduce la calidad editorial.'
    return info

def diagnose():
    checks=[]
    def check(name, fn):
        try:detail=fn();checks.append({'name':name,'ok':True,'detail':str(detail)[:1200]})
        except Exception as e:checks.append({'name':name,'ok':False,'detail':str(e)[:1200]})
    def require_tool(name, minimum=None):
        p=binary(name)
        if not p:raise RuntimeError('No encontrado. Usa Instalar / actualizar.')
        out=run([p,'--version' if name in ('node','codex') else '-version'])
        if minimum and version(out)<minimum:raise RuntimeError(f'Versión insuficiente: {out[:100]}')
        return out.splitlines()[0]
    def ff():
        require_tool('ffmpeg');require_tool('ffprobe')
        if Path(binary('ffmpeg')).parent.resolve()!=Path(binary('ffprobe')).parent.resolve():raise RuntimeError('ffmpeg y ffprobe deben pertenecer a la misma instalación.')
        filters=run([binary('ffmpeg'),'-hide_banner','-filters'])
        missing=[x for x in ('zscale','tonemap','loudnorm','sidechaincompress') if not re.search(r'\b'+x+r'\b',filters)]
        if missing:raise RuntimeError('FFmpeg incompleto: faltan '+', '.join(missing))
        return require_tool('ffmpeg')+'; filtros de color y mezcla disponibles'
    def hf():
        cmd,v=hf_command();result=json.loads(run(cmd+['doctor','--json'],env=environment(),timeout=120))
        if not result.get('ok'):raise RuntimeError(json.dumps(result,ensure_ascii=False)[-1100:])
        return f'HyperFrames {v}: doctor ok (no certifica un render)'
    def audio():
        if not local_python().is_file():raise RuntimeError('Falta entorno aislado de audio / ASR.')
        run([local_python(),'-c','import numpy,scipy,soundfile,pystoi,faster_whisper; from ai_edge_litert.interpreter import Interpreter'],timeout=90)
        script=ROOT/'proyecto/Framework-Edicion-Social/scripts/audio_multimedia.py'
        report=run([local_python(),script,'doctor'],env=environment(),timeout=90)
        inference="import sys,numpy as np; from ai_edge_litert.interpreter import Interpreter; m=Interpreter(model_path=sys.argv[1],num_threads=2); m.allocate_tensors(); i=m.get_input_details()[0]; m.set_tensor(i['index'],np.zeros(i['shape'],dtype=i['dtype'])); m.invoke(); x=m.get_tensor(m.get_output_details()[0]['index']); assert np.isfinite(x).all() and x.size>0; print('YAMNet: carga e inferencia local correctas')"
        probe=run([local_python(),'-c',inference,ROOT/'runtime/models/yamnet/model.tflite'],env=environment(),timeout=90)
        return report+'; '+probe
    def templates():
        p=ROOT/read(ROOT/'kit-config.json')['templates'];data=read(p)
        if len(data['templates'])!=30:raise RuntimeError('Catálogo incompleto')
        for t in data['templates']:
            for suffix in ('.svg','.png'):
                if not (p.parent/t['artifact']).with_suffix(suffix).is_file():raise RuntimeError('Falta tablero '+t['id'])
        return '30 propuestas, tableros y reglas presentes'
    def skills():
        required=('hyperframes','hyperframes-core','hyperframes-cli','general-video','media-use','visual-quality-director')
        for s in required:
            if not (ROOT/'proyecto/.agents/skills'/s/'SKILL.md').is_file():raise RuntimeError('Falta skill '+s)
        return 'Skills de edición incluidas dentro del proyecto'
    def writable():
        with tempfile.TemporaryFile(dir=ROOT) as f:f.write(b'ok')
        return 'Carpeta con permiso de escritura'
    if os.name=='nt':
        def vc():
            base=Path(os.environ.get('SystemRoot','C:/Windows'))/'System32'
            if not all((base/x).exists() for x in ('vcruntime140.dll','msvcp140.dll')):raise RuntimeError('Falta Microsoft Visual C++ x64 para los motores de audio/ASR.')
            return 'Bibliotecas base de Microsoft Visual C++ presentes; el import del motor comprueba el uso real.'
        check('Visual C++ (Windows)',vc)
    check('Carpeta',writable)
    check('Python',lambda:sys.version if sys.version_info>=(3,11) else (_ for _ in ()).throw(RuntimeError('Requiere Python 3.11+')))
    check('Node',lambda:require_tool('node',(22,0,0)))
    check('FFmpeg',ff);check('Plantillas',templates);check('Skills',skills);check('HyperFrames y Chrome',hf);check('Audio asistido',audio)
    check('ASR local',lambda:run([local_python(),ROOT/'tools/transcribir.py','--check'],env=environment(),timeout=120))
    base_ok=all(c['ok'] for c in checks)
    result={'checked_at':now(),'hardware':hardware(),'checks':checks,'dependencies_ok':base_ok,
        'message':'Dependencias verificadas. Falta prueba de render en este equipo y acceso a Codex.' if base_ok else 'Hay requisitos pendientes. Puedes preparar el contexto mientras los resuelves.',
        'human_listening':'por confirmar','render_verified':False}
    save(ROOT/'resultados/diagnostico-actual.json',result)
    return result

def npm_cmd():
    node=binary('node')
    if not node:raise RuntimeError('Instala Node primero.')
    candidates=[Path(node).parent/'node_modules/npm/bin/npm-cli.js',Path(node).parent.parent/'lib/node_modules/npm/bin/npm-cli.js']
    for p in candidates:
        if p.is_file():return [node,str(p)]
    npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm')
    if not npm:raise RuntimeError('Falta npm junto a Node.')
    # npm.cmd is never given user-authored arguments; prefer npm JS on Windows.
    return [npm]

def installation_plan(kind, releases):
    if time.time()-releases.get('checked_epoch',0)>600:raise ValueError('Consulta de nuevo las versiones: la verificación tiene más de 10 minutos.')
    if kind not in ('node','hyperframes','ffmpeg','audio','asr','codex','vcredist'):raise ValueError('Instalación desconocida')
    r=releases['releases'];p={'id':uuid.uuid4().hex,'kind':kind,'created_at':time.time(),'source':'','scope':'carpeta de esta entrega','steps':[]}
    if kind=='node':
        v=r['node'].get('version')
        if not v or not re.fullmatch(r'\d+\.\d+\.\d+',v):raise ValueError('No se pudo consultar la versión actual de Node. Reintenta con conexión.')
        arch={'arm64':'arm64','aarch64':'arm64','amd64':'x64','x86_64':'x64'}.get(platform.machine().lower())
        if not arch:raise ValueError('Arquitectura no soportada por este instalador')
        target=f'node-v{v}-'+('win' if os.name=='nt' else 'darwin')+'-'+arch
        p.update(version=v,target=target,source=f'https://nodejs.org/dist/v{v}/',steps=['Descargar Node estable '+v+' y verificar SHA-256 oficial.','Extraer en runtime/node; usarlo solo en esta entrega.'])
    elif kind=='hyperframes':
        v=r['hyperframes'].get('version')
        if not v or not re.fullmatch(r'\d+\.\d+\.\d+',v):raise ValueError('No se pudo consultar la versión actual de HyperFrames.')
        npm_cmd();p.update(version=v,source=SOURCES['hyperframes'],steps=[f'Instalar hyperframes@{v} y GSAP en runtime/hyperframes/{v}.','Descargar/preparar Chrome administrado por HyperFrames. Su caché puede quedar en la cuenta del usuario.','Registrar esta versión para los nuevos lotes; conservar versiones de lotes existentes.'])
    elif kind=='ffmpeg':
        if os.name=='nt':
            exe=shutil.which('winget')
            if not exe:raise ValueError('Falta App Installer / winget. Instálalo desde Microsoft Store y vuelve a abrir este asistente.')
            p.update(source='https://github.com/microsoft/winget-pkgs/tree/master/manifests/g/Gyan/FFmpeg',scope='instalación administrada por winget en Windows',commands=[[exe,'install','--id','Gyan.FFmpeg','--exact','--source','winget','--accept-source-agreements','--accept-package-agreements']],steps=['winget consultará e instalará la versión vigente de Gyan.FFmpeg (full); puede pedir permiso de Windows.','Volver a diagnosticar filtros HDR y audio, y reiniciar el asistente si cambia PATH.'])
        else:
            exe=shutil.which('brew') or next((str(p) for p in (Path('/opt/homebrew/bin/brew'),Path('/usr/local/bin/brew')) if p.is_file()),None)
            if not exe:raise ValueError('Falta Homebrew. Abre https://brew.sh e instálalo con su asistente oficial; luego vuelve aquí.')
            installed=subprocess.run([exe,'list','--versions','ffmpeg-full'],capture_output=True).returncode==0
            p.update(source='https://formulae.brew.sh/formula/ffmpeg-full',scope='Homebrew del equipo: puede actualizar esa fórmula y sus dependencias',commands=[[exe,'update'],[exe,'upgrade' if installed else 'install','ffmpeg-full']],steps=['Actualizar el catálogo Homebrew.','Instalar/actualizar ffmpeg-full. Verificar filtros antes de usarlo.'])
    elif kind=='vcredist':
        if os.name!='nt':raise ValueError('Visual C++ corresponde solo a Windows.')
        p.update(source='https://aka.ms/vs/17/release/vc_redist.x64.exe',scope='Microsoft Visual C++ Redistributable x64 en Windows',steps=['Descargar el instalador oficial vigente de Microsoft.','Ejecutarlo en modo interactivo: revisa sus permisos y condiciones.','Repetir diagnóstico e importación del motor de audio.'])
    elif kind=='audio':
        p.update(source='https://astral.sh/uv/ + https://pypi.org/ + fuentes de YAMNet registradas en el framework',steps=['Descargar uv de Astral y Python 3.12 (último parche compatible) dentro de esta entrega si hacen falta. Crear runtime/audio. Instalar el entorno compatible con la calibración: numpy 2.4.6, scipy 1.17.1, soundfile 0.14.0, pystoi 0.4.1, ai-edge-litert 2.2.0, y la última versión compatible de faster-whisper.','Descargar YAMNet y etiquetas (≈4.2 MB), verificar los hashes originales.','Conservar estas versiones calibradas: actualizar modelos/librerías exige una nueva calibración. Si no hay wheels para este Python/OS se informará, sin compilar silenciosamente.'])
    elif kind=='asr':
        if not local_python().is_file():raise ValueError('Prepara audio primero.')
        p.update(source='https://huggingface.co/Systran/faster-whisper-small',steps=['Descargar modelo Whisper small multilingüe (cientos de MB) en runtime/models/whisper-small.','Usar CPU int8 como opción común a ambas PC y Mac; CUDA es opcional y no se instala.','Cargar el modelo localmente para comprobarlo. Los masters no se envían a la red.'])
    else:
        v=r['codex'].get('version')
        if not v or not re.fullmatch(r'\d+\.\d+\.\d+(?:[-.\w]*)?',v):raise ValueError('No se pudo consultar Codex.')
        npm_cmd();p.update(version=v,source=SOURCES['codex'],steps=[f'Instalar Codex CLI {v} en runtime/codex.','El inicio de sesión es personal y se realiza después; no se transfieren credenciales.'])
    return p

def download(url, path):
    path.parent.mkdir(parents=True,exist_ok=True)
    req=urllib.request.Request(url,headers={'User-Agent':'Edicion-Portable/2.0'})
    try:
        with urllib.request.urlopen(req,timeout=120) as source,path.open('wb') as dest:shutil.copyfileobj(source,dest)
    except urllib.error.URLError as e:
        if not isinstance(e.reason,ssl.SSLCertVerificationError):raise
        curl='/usr/bin/curl' if sys.platform=='darwin' else shutil.which('curl.exe' if os.name=='nt' else 'curl')
        if not curl:raise
        run([curl,'--fail','--location','--proto','=https','--proto-redir','=https','--max-time','600','--output',path,url],timeout=620)

def perform(plan, authorized=False):
    if not authorized:raise PermissionError('La instalación requiere autorización explícita del usuario.')
    if time.time()-plan['created_at']>600:raise ValueError('Plan vencido. Vuelve a consultar versiones.')
    c=config();kind=plan['kind'];env=environment();started=time.monotonic()
    log=ROOT/'resultados/instalaciones'/(now().replace(':','')+'-'+plan['id']+'.json')
    receipt={'plan':plan,'authorized':True,'start':now(),'status':'running'};save(log,receipt)
    try:
        if kind=='node':
            target=plan['target'];ext='.zip' if os.name=='nt' else '.tar.gz';name=target+ext
            hashes=request(plan['source']+'SHASUMS256.txt').decode()
            expected=next((line.split()[0] for line in hashes.splitlines() if line.split()[-1]==name),None)
            if not expected:raise RuntimeError('Archivo ausente del manifiesto oficial de Node.')
            with tempfile.TemporaryDirectory(dir=ROOT) as td:
                archive=Path(td)/name;download(plan['source']+name,archive)
                if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected:raise RuntimeError('SHA-256 de Node incorrecto')
                dest=ROOT/'runtime/node';dest.mkdir(parents=True,exist_ok=True)
                if ext=='.zip':
                    with zipfile.ZipFile(archive) as z:
                        if any(not (dest/n).resolve().is_relative_to(dest.resolve()) for n in z.namelist()):raise ValueError('Ruta de archivo inválida')
                        z.extractall(dest)
                else:
                    with tarfile.open(archive) as z:z.extractall(dest,filter='data')
            c['node']=str(dest/target/('node.exe' if os.name=='nt' else 'bin/node'));save(ROOT/'runtime.local.json',c)
        elif kind in ('hyperframes','codex'):
            v=plan['version'];dest=ROOT/'runtime'/kind/(v if kind=='hyperframes' else '')
            dest.mkdir(parents=True,exist_ok=True)
            package='hyperframes@'+v if kind=='hyperframes' else '@openai/codex@'+v
            args=npm_cmd()+['install','--prefix',str(dest),'--no-audit','--no-fund','--save-exact',package]
            if kind=='hyperframes':args+=['gsap']
            receipt['output']=run(args,timeout=1200,env=env)[-5000:]
            if kind=='hyperframes':
                cmd=windows.cli({'hyperframes':v},{'node':binary('node')})
                receipt['browser']=run(cmd+['browser','ensure'],env=env,timeout=1200)[-5000:]
                c['hyperframes']=v;save(ROOT/'runtime.local.json',c)
        elif kind=='ffmpeg':
            receipt['output']='\n'.join(run(cmd,timeout=1800,env=env) for cmd in plan['commands'])[-7000:]
            for key in ('ffmpeg','ffprobe'):c.pop(key,None)
            save(ROOT/'runtime.local.json',c)
        elif kind=='vcredist':
            installer=ROOT/'runtime/downloads/vc_redist.x64.exe';download(plan['source'],installer)
            receipt['output']=run([installer,'/install'],timeout=1800)
        elif kind=='audio':
            uvdir=ROOT/'runtime/uv';uv=uvdir/('uv.exe' if os.name=='nt' else 'uv')
            env.update(UV_UNMANAGED_INSTALL=str(uvdir),UV_PYTHON_INSTALL_DIR=str(ROOT/'runtime/python'),UV_CACHE_DIR=str(ROOT/'runtime/uv-cache'))
            # Only reached after explicit authorization of this plan, including uv/Python.
            if not uv.is_file():
                ext='ps1' if os.name=='nt' else 'sh';installer=ROOT/'runtime/downloads'/('uv-install.'+ext)
                download('https://astral.sh/uv/install.'+ext,installer)
                command=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',installer] if os.name=='nt' else ['/bin/sh',installer]
                run(command,timeout=300,env=env)
            run([uv,'python','install','3.12'],timeout=600,env=env)
            dest=ROOT/'runtime/audio'
            # Never overwrite an environment from a different host or Python.
            if dest.exists():
                backup=dest.with_name('audio-anterior-'+time.strftime('%Y%m%d-%H%M%S'))
                dest.rename(backup)
            run([uv,'venv','--python','3.12','--seed',dest],timeout=180,env=env)
            py=local_python();req=ROOT/'proyecto/Framework-Edicion-Social/research/escucha-perceptual-2026-10-01/evidencia/requirements-core.txt'
            receipt['output']=run([py,'-m','pip','install','--only-binary=:all:','-r',req,'faster-whisper'],timeout=1800,env=env)[-6000:]
            records=read(ROOT/'proyecto/Framework-Edicion-Social/research/escucha-perceptual-2026-10-01/modelo/descarga-yamnet.json')
            for rec in records:
                dest=ROOT/'runtime/models/yamnet'/Path(rec['file']).name
                if not dest.exists() or hashlib.sha256(dest.read_bytes()).hexdigest()!=rec['sha256']:
                    temp=dest.with_suffix(dest.suffix+'.download');download(rec['source'],temp)
                    if hashlib.sha256(temp.read_bytes()).hexdigest()!=rec['sha256']:temp.unlink();raise RuntimeError('Modelo/etiquetas cambiaron; revisión requerida.')
                    temp.replace(dest)
            receipt['doctor']=run([py,ROOT/'proyecto/Framework-Edicion-Social/scripts/audio_multimedia.py','doctor'],env=env,timeout=90)
            receipt['lock']=run([py,'-m','pip','freeze'],env=env)
            (ROOT/'runtime/audio/requirements-resolved.txt').write_text(receipt['lock'],encoding='utf-8')
        else:
            code="from faster_whisper import WhisperModel; import sys; WhisperModel('small',device='cpu',compute_type='int8',download_root=sys.argv[1]); print('Modelo descargado y cargado')"
            receipt['output']=run([local_python(),'-c',code,ROOT/'runtime/models/whisper-small'],timeout=1800,env=env)
        receipt['status']='pass'
    except Exception as e:receipt.update(status='fail',error=str(e));raise
    finally:receipt['seconds']=round(time.monotonic()-started,3);save(log,receipt)
    return receipt
