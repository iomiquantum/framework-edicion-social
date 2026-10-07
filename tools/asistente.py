#!/usr/bin/env python3
"""Loopback-only wizard; per-session capability, origin checks and explicit install plans."""
from __future__ import annotations
import argparse, sys, hashlib, http.server, json, mimetypes, os, secrets, shutil, threading, time, urllib.parse, urllib.request, webbrowser, base64, re
from pathlib import Path
import onboarding as ob
import runtime_setup as rt
import progreso as progress
ROOT=Path(__file__).resolve().parents[1]
TOKEN=secrets.token_urlsafe(32)
STATE={'job':None,'versions':None,'plans':{},'diagnosis':None,'smoke':None}
BUSY=threading.Lock()

def smoke():
    """A tiny technical test, never a render or approval of the person's new video."""
    cmd,v=rt.hf_command();env=rt.environment();ff=rt.binary('ffmpeg');probe=rt.binary('ffprobe')
    if not ff or not probe:raise ValueError('Completa FFmpeg primero.')
    dest=ROOT/'resultados/prueba-equipo'/time.strftime('%Y%m%d-%H%M%S');dest.mkdir(parents=True)
    package=ROOT/'runtime/hyperframes'/v/'node_modules/gsap/dist/gsap.min.js'
    if not package.exists():raise ValueError('Prepara HyperFrames y GSAP primero.')
    shutil.copy2(package,dest/'gsap.min.js')
    rt.run([ff,'-v','error','-f','lavfi','-i','sine=frequency=440:duration=1','-ar','48000',dest/'tono.wav'])
    (dest/'index.html').write_text('''<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;width:100%;height:100%;overflow:hidden}#root{width:100%;height:100%;position:relative;background:#102d40}.box{position:absolute;left:30px;top:180px;width:80px;height:80px;background:#eff5f4}</style><script src="gsap.min.js"></script></head><body><div id="root" data-composition-id="setup-test" data-width="360" data-height="640" data-duration="1"><div class="box"></div><audio id="test-tone" class="clip" data-start="0" data-duration="1" data-track-index="1" src="tono.wav"></audio></div><script>window.__timelines=window.__timelines||{};window.__timelines['setup-test']=gsap.timeline({paused:true}).to('.box',{x:180,duration:1,ease:'none'});</script></body></html>''',encoding='utf-8')
    evidence={'version':v,'platform':rt.hardware(),'at':rt.now(),'scope':'Prueba técnica sintética de 1 s; no QA ni aprobación de video real.'}
    evidence['check']=rt.run(cmd+['check',str(dest)],env=env,timeout=180)[-6000:]
    evidence['render']=rt.run(cmd+['render',str(dest),'--output',str(dest/'prueba.mp4'),'--workers','1'],env=env,timeout=360)[-6000:]
    data=json.loads(rt.run([probe,'-v','error','-show_streams','-show_format','-of','json',dest/'prueba.mp4']))
    if not any(x['codec_type']=='audio' for x in data['streams']) or not any(x['codec_type']=='video' for x in data['streams']):raise RuntimeError('Prueba sin video o audio.')
    if not .8<float(data['format']['duration'])<1.5:raise RuntimeError('Duración de prueba inesperada.')
    # Decode the actual output and verify motion, not just a successful command exit.
    import subprocess
    decoded=subprocess.run([ff,'-v','error','-i',str(dest/'prueba.mp4'),'-vf','fps=4,scale=36:64','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout
    size=36*64*3
    if len(decoded)<size*2 or decoded[:size]==decoded[-size:]:raise RuntimeError('La prueba no conserva movimiento visible.')
    import array, math
    raw_audio=subprocess.run([ff,'-v','error','-i',str(dest/'prueba.mp4'),'-vn','-ac','1','-ar','16000','-f','f32le','-'],capture_output=True,check=True).stdout
    samples=array.array('f');samples.frombytes(raw_audio)
    rms=math.sqrt(sum(x*x for x in samples)/max(1,len(samples)))
    if not math.isfinite(rms) or rms<.001:raise RuntimeError('La pista de la prueba está vacía o en silencio.')
    evidence.update(status='pass',probe=data,decoded_motion=True,audio_rms=rms,dependencies_fingerprint=fingerprint())
    rt.save(dest/'recibo.json',evidence);rt.save(ROOT/'resultados/prueba-equipo-actual.json',evidence)
    return evidence

def fingerprint():
    c=rt.config();paths={k:rt.binary(k) for k in ('node','ffmpeg','ffprobe')}
    stamps={k:[v,Path(v).stat().st_size,Path(v).stat().st_mtime_ns] if v else None for k,v in paths.items()}
    return hashlib.sha256(json.dumps({'paths':stamps,'hf':c.get('hyperframes'),'os':os.name,'machine':rt.hardware()['cpu']},sort_keys=True).encode()).hexdigest()

def job(fn, name='tarea'):
    if not BUSY.acquire(False):raise ValueError('Hay una tarea en curso. Espera su resultado.')
    STATE['job']={'status':'running','started':rt.now()}
    def target():
        try:
            progress.event(name,'running')
            result=fn()
            progress.event(name,'pass')
            STATE['job']={'status':'pass','result':result}
        except Exception as e:
            STATE['job']={'status':'fail','error':str(e)}
            try:progress.event(name,'fail',str(e))
            except OSError:pass
        finally:BUSY.release()
    threading.Thread(target=target,daemon=True).start()
    return {'status':'running'}

class Handler(http.server.BaseHTTPRequestHandler):
    server_version='EdicionPortable/2'
    def log_message(self,*a):pass
    def send(self,data,kind='application/json',status=200):
        if kind=='application/json':data=json.dumps(data,ensure_ascii=False).encode()
        elif isinstance(data,str):data=data.encode()
        self.send_response(status);self.send_header('Content-Type',kind+'; charset=utf-8');self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer')
        hashes=''
        if kind=='text/html':
            hashes=' '.join("'sha256-"+base64.b64encode(hashlib.sha256(s).digest()).decode()+"'" for s in re.findall(rb'<script(?:\s[^>]*)?>(.*?)</script>',data,re.S))
        self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' "+hashes+"; frame-ancestors 'none'; object-src 'none'; base-uri 'none'")
        self.end_headers();self.wfile.write(data)
    def authorized(self):
        expected=f'127.0.0.1:{self.server.server_port}'
        if self.headers.get('Host')!=expected:return False
        if self.headers.get('Origin') not in (None,'http://'+expected):return False
        return secrets.compare_digest(self.headers.get('X-Setup-Token',''),TOKEN)
    def do_GET(self):
        try:
            parsed=urllib.parse.urlparse(self.path);path=parsed.path;q=urllib.parse.parse_qs(parsed.query)
            if self.headers.get('Host')!=f'127.0.0.1:{self.server.server_port}':return self.send({'error':'Host inválido'},status=403)
            if path=='/':return self.send((ROOT/'asistente/index.html').read_bytes(),'text/html')
            if path in ('/grabacion','/GUIA_GRABACION_MASTER.html'):return self.send((ROOT/'GUIA_GRABACION_MASTER.html').read_bytes(),'text/html')
            if path in ('/guia','/GUIASUPERDETALLADA.html'):return self.send((ROOT/'GUIASUPERDETALLADA.html').read_bytes(),'text/html')
            if path=='/asistente/progreso.js':return self.send((ROOT/'asistente/progreso.js').read_bytes(),'text/javascript')
            if path in ('/LEEME.md','/INICIO%20Y%20CONFIGURACION%20DE%20FRAMEWORK.md'):
                return self.send((ROOT/urllib.parse.unquote(path[1:])).read_bytes(),'text/plain')
            if path in ('/app.js','/style.css'):
                return self.send((ROOT/'asistente'/path[1:]).read_bytes(),'text/javascript' if path.endswith('.js') else 'text/css')
            if path.startswith('/assets/'):
                name=Path(path).name;base=(ROOT/rt.read(ROOT/'kit-config.json')['templates']).parent/'assets-compartidos'
                if path!='/assets/'+name or not (base/name).is_file():raise ValueError('Recurso no encontrado')
                return self.send((base/name).read_bytes(),mimetypes.guess_type(name)[0] or 'application/octet-stream')
            if path=='/board':
                p=ob.selected_palette({'palette':q.get('palette',['bosque'])[0],'colors':json.loads(q['colors'][0]) if 'colors' in q else None}) if 'palette' in q or 'colors' in q else None
                return self.send(ob.board(q.get('template',['T01'])[0],p,embed=True),'image/svg+xml')
            if not self.authorized():return self.send({'error':'Sesión inválida. Abre el enlace de la terminal.'},status=403)
            if path=='/api/ping':return self.send({'root':str(ROOT),'status':'running'})
            if path=='/api/progress-copies':return self.send(progress.copies())
            if path=='/api/progress-copy':return self.send(progress.copies(q.get('name',[''])[0]))
            if path=='/api/next-video':return self.send({'next_video':max([30]+[int(row['video']) for row in rt.read(ROOT/'proyectos.json')])+1})
            if path.startswith('/api/progress/'):return self.send(progress.read(path.removeprefix('/api/progress/')))
            if path=='/api/info':
                return self.send({'root':str(ROOT),'workspace':str(ROOT/'proyecto'),'hardware':rt.hardware(),'catalog':ob.catalog(),'job':STATE['job'],'runtime':rt.config(),'styles':rt.read(ROOT/'proyecto/Framework-Edicion-Social/styles/catalog.json'),'entry':str(ROOT/'entrada-masters'),'next_video':max([30]+[int(row['video']) for row in rt.read(ROOT/'proyectos.json')])+1})
            if path=='/api/job':return self.send(STATE['job'] or {'status':'idle'})
            return self.send({'error':'No encontrado'},status=404)
        except Exception as e:self.send({'error':str(e)},status=400)
    def do_POST(self):
        if not self.authorized():return self.send({'error':'Origen o sesión no autorizados'},status=403)
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=500000:raise ValueError('Tamaño de solicitud inválido')
            data=json.loads(self.rfile.read(length));path=urllib.parse.urlparse(self.path).path
            if path=='/api/progress-backup':
                if data.get('kind') not in ('guia','grabacion','borrador'):raise ValueError('Tipo de copia inválido.')
                return self.send(progress.backup(data['kind'],data['data']))
            if path in ('/api/progress/guia','/api/progress/borrador','/api/progress/grabacion'):
                if type(data.get('revision')) is not int:raise ValueError('Falta la revisión del progreso.')
                return self.send(progress.write(path.removeprefix('/api/progress/'),data['data'],data['revision']))
            if path=='/api/diagnose':
                def diag():
                    d=rt.diagnose();STATE['diagnosis']=d;return d
                return self.send(job(diag,'diagnostico'))
            if path=='/api/versions':
                def versions():
                    STATE['versions']=rt.latest();rt.save(ROOT/'resultados/versiones-consultadas.json',STATE['versions']);return STATE['versions']
                return self.send(job(versions,'consulta-versiones'))
            if path=='/api/plan':
                if not STATE['versions']:raise ValueError('Consulta versiones antes de preparar una instalación.')
                p=rt.installation_plan(data['kind'],STATE['versions']);STATE['plans'][p['id']]=p;return self.send(p)
            if path=='/api/install':
                if data.get('authorize') is not True:raise ValueError('Confirma la autorización antes de descargar.')
                if BUSY.locked():raise ValueError('Espera la tarea actual.')
                p=STATE['plans'].pop(data.get('id'),None)
                if not p:raise ValueError('Plan desconocido o ya utilizado')
                STATE['diagnosis']=None;STATE['smoke']=None
                return self.send(job(lambda:rt.perform(p,authorized=True),'instalacion-'+p['kind']))
            if path=='/api/smoke':
                if data.get('authorize') is not True:raise ValueError('Autoriza la prueba de 1 segundo.')
                def test():STATE['smoke']=smoke();return STATE['smoke']
                return self.send(job(test,'prueba-render'))
            if path=='/api/palettes':return self.send(ob.suggestions(str(data.get('context',''))[:20000]))
            if path=='/api/prepare':
                def prepare():
                    result=ob.prepare(data)
                    try:progress.write('ultimo-lote',result)
                    except Exception as e:result.setdefault('warnings',[]).append('Lote creado; no se pudo guardar el acceso reciente: '+str(e)+'. Usa ABRIR_EN_CODEX.txt dentro del lote.')
                    return result
                return self.send(job(prepare,'preparar-lote'))
            if path=='/api/ready':
                d=STATE['diagnosis'];s=STATE['smoke']
                ok=bool(d and d['dependencies_ok'] and s and s.get('status')=='pass' and s.get('dependencies_fingerprint')==fingerprint() and data.get('codex_signed_in') is True)
                return self.send({'ready':ok,'codex_verification':'confirmado por el usuario' if data.get('codex_signed_in') else 'pendiente','message':'Ya tienes todo listo para empezar a editar. Abre Codex y continúa con el lote preparado.' if ok else 'Puedes preparar el lote. Para confirmar que todo está listo, completa diagnóstico, prueba de render e inicio de sesión en Codex.'})
            return self.send({'error':'Acción no encontrada'},status=404)
        except progress.Conflict as e:self.send({'error':str(e)},status=409)
        except Exception as e:self.send({'error':str(e)},status=400)

def main():
    p=argparse.ArgumentParser();p.add_argument('--no-browser',action='store_true');p.add_argument('--codex',action='store_true');p.add_argument('--edit',nargs=argparse.REMAINDER);p.add_argument('--port',type=int,default=0);args=p.parse_args()
    if args.edit:
        sys.argv=[str(ROOT/'tools/windows.py'),*args.edit]
        rt.windows.main();return
    if args.codex:
        from abrir_codex import main as open_codex
        open_codex();return
    if not args.port:
        try:
            prior=rt.read(ROOT/'MI-PROGRESO/sesion.json');port=prior['port'];token=prior['token']
            if prior['root']!=str(ROOT) or type(port) is not int or not 1<=port<=65535 or not re.fullmatch(r'[A-Za-z0-9_-]{30,80}',token):raise ValueError('Otra ubicación o sesión')
            request=urllib.request.Request(f'http://127.0.0.1:{port}/api/ping',headers={'X-Setup-Token':token})
            with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request,timeout=1.5) as response:reply=json.load(response)
            if reply.get('root')==str(ROOT):
                url=f'http://127.0.0.1:{port}/guia#{token}'
                print('El asistente ya estaba abierto. Conserva su primera terminal.\n'+url,flush=True)
                if not args.no_browser:webbrowser.open(url)
                return
        except (OSError,ValueError,KeyError,TypeError):pass
    if not (ROOT/'proyectos.json').exists():rt.save(ROOT/'proyectos.json',[])
    (ROOT/'entrada-masters').mkdir(exist_ok=True)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    url=f'http://127.0.0.1:{server.server_port}/guia#{TOKEN}'
    folder=ROOT/'MI-PROGRESO';folder.mkdir(exist_ok=True)
    progress.atomic(folder/'sesion.json',{'root':str(ROOT),'port':server.server_port,'token':TOKEN})
    # Local session shortcut: excluded from Git; the token never appears in a remote request.
    shortcut='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><title>Abrir guía</title><body style="font:20px/1.6 system-ui;max-width:750px;margin:60px auto;padding:24px;background:#f7f6ef;color:#203c38"><h1>Volver a mi guía</h1><p>Deja la ventana de INICIO abierta. Pulsa el botón para recuperar el progreso guardado en esta carpeta.</p><p><a style="display:inline-block;background:#225f51;color:white;padding:16px 24px;border-radius:12px" href="'''+url+'''">ABRIR GUÍA E INICIAR</a></p><p>Si el navegador dice que no puede conectar, cierra esta página y abre de nuevo INICIO WINDOWS.cmd o INICIO MAC.command. Después vuelve a abrir este acceso.</p><p><a href="../GUIASUPERDETALLADA.html">Leer la guía sin el asistente</a></p></body></html>'''
    (folder/'ABRIR GUIA.html').write_text(shortcut,encoding='utf-8')
    print('INICIO Y CONFIGURACION DE FRAMEWORK\n'+url+'\nDeja esta terminal abierta. Ctrl+C cierra el asistente.\nSi el navegador no abre: doble clic en MI-PROGRESO/ABRIR GUIA.html y pulsa ABRIR GUIA E INICIAR.\nEl progreso se guarda en MI-PROGRESO dentro de esta misma carpeta.',flush=True)
    if not args.no_browser:
        try:
            if not webbrowser.open(url):print('No se pudo abrir el navegador automáticamente. Usa el acceso HTML indicado arriba.',flush=True)
        except Exception:print('Abre MI-PROGRESO/ABRIR GUIA.html para continuar.',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
