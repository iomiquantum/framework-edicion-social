"""Context, palette previews and atomic preparation of new editing batches."""
from __future__ import annotations
import base64, struct
import colorsys, hashlib, html, json, os, re, shutil, time, unicodedata, uuid
from collections import Counter
from pathlib import Path
import runtime_setup as rt
import windows
ROOT=Path(__file__).resolve().parents[1]
PALETTES=[
 ('bosque','Bosque editorial',['#0D3028','#F2F2DE','#DA8138','#8BC0A0'],['salud','bienestar','sostenibilidad','educacion','confianza']),
 ('vino','Vino y porcelana',['#3D1433','#FFF0E6','#A52959','#E6BC79'],['marca','historia','liderazgo','ventas','personal']),
 ('cobre','Cobre de estudio',['#27252D','#F5E6D1','#AB4C28','#E9BA6A'],['negocio','finanzas','estrategia','profesional']),
 ('oceano','Océano mineral',['#102D40','#EFF5F4','#246B79','#94D6B4'],['tecnologia','ia','datos','educacion']),
 ('ciruela','Ciruela y lima suave',['#302440','#F1EDDD','#754C88','#CADA86'],['creatividad','diseno','marketing','redes']),
 ('terracota','Terracota y oliva',['#342B22','#FBF2DF','#B74C31','#C9C58D'],['comida','vida','humano','cercano']),
 ('petroleo','Petróleo y albaricoque',['#173B3F','#F6ECE0','#2F6B69','#F5B282'],['ventas','empresa','gestion','productividad']),
 ('tinta','Tinta y lavanda',['#242938','#F5F0F7','#63549D','#C7B9EB'],['innovacion','ia','tecnologia','futuro']),
 ('cacao','Cacao y salvia',['#382920','#FFF4E2','#806347','#B8C9A4'],['historia','educacion','experiencia','bienestar']),
 ('granada','Granada y arena',['#3D2027','#FCF0DC','#AF394C','#E5BA82'],['emprendimiento','marketing','energia','negocio']),
]
def normalize(s):return ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c))
def catalog():return rt.read(ROOT/rt.read(ROOT/'kit-config.json')['templates'])
def palette(pid):
    row=next((p for p in PALETTES if p[0]==pid),None)
    if not row:raise ValueError('Paleta desconocida')
    return {'id':row[0],'name':row[1],'colors':row[2],'roles':['ink','paper','accent','soft'],'tags':row[3]}
def suggestions(context):
    history=ROOT/'asistente/historial-paletas.json';used=rt.read(history) if history.exists() else []
    text=normalize(context);ids=[x.get('palette') for x in used]
    ranked=sorted(PALETTES,key=lambda p:(p[0] in ids[-5:],-sum(t in text for t in p[3]),hashlib.sha256((text+p[0]).encode()).hexdigest()))
    return [{**palette(p[0]),'reason':'Afinidad por tema y tono; propuesta orientativa, no inferencia sobre tu audiencia.','used_before':p[0] in ids} for p in ranked[:5]]
def contrast(a,b):
    def lum(c):
        x=[int(c[i:i+2],16)/255 for i in (1,3,5)];x=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in x]
        return sum(v*w for v,w in zip(x,[.2126,.7152,.0722]))
    a,b=sorted([lum(a),lum(b)]);return (b+.05)/(a+.05)
def selected_palette(data):
    p=palette(data.get('palette','bosque'))
    custom=data.get('colors')
    if custom:
        if not isinstance(custom,list) or len(custom)!=4 or not all(isinstance(x,str) and re.fullmatch('#[0-9A-Fa-f]{6}',x) for x in custom):raise ValueError('Usa cuatro colores HEX válidos.')
        if custom!=p['colors']:p={**p,'customized':True,'name':p['name']+' · ajustada','colors':custom}
    if contrast(p['colors'][0],p['colors'][1])<4.5:raise ValueError('Texto y fondo necesitan contraste mínimo 4.5:1. Oscurece la tinta o aclara el fondo.')
    return p

def board(template_id, pal=None, embed=False):
    item=next((t for t in catalog()['templates'] if t['id']==template_id),None)
    if not item:raise ValueError('Plantilla desconocida')
    base=(ROOT/rt.read(ROOT/'kit-config.json')['templates']).parent
    source=(base/item['artifact']).with_suffix('.svg').read_text(encoding='utf-8')
    # Raster photography stays intact; only vector tokens change. Every preview is separate.
    width,height=struct.unpack('>II',(base/item['artifact']).read_bytes()[16:24])
    # Original PNGs were exported with a cropped canvas; match that viewport only.
    source=re.sub(r'(<svg[^>]*\bheight=)"[^"]+"',lambda m:m[1]+f'"{height}"',source,count=1)
    source=re.sub(r'viewBox="[^"]+"',f'viewBox="0 0 {width} {height}"',source,count=1)
    source=source.replace('../assets-compartidos/','/assets/')
    if embed:
        def image_ref(match):
            name=match[1];path=base/'assets-compartidos'/name
            if path.parent.resolve()!=(base/'assets-compartidos').resolve() or not path.is_file():raise ValueError('Imagen de tablero no encontrada')
            mime='image/png' if path.suffix.lower()=='.png' else 'image/jpeg'
            return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()
        source=re.sub(r'/assets/([^"<>]+)',image_ref,source)
    if not pal:return source
    ink,paper,accent,soft=pal['colors'];tokens=Counter(re.findall(r'#[0-9a-fA-F]{6}\b',source))
    mapped={}
    for color in tokens:
        rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)];h,l,s=colorsys.rgb_to_hls(*rgb)
        brightness=sum(v*w for v,w in zip(rgb,[.2126,.7152,.0722]))
        mapped[color]=ink if l<.27 else paper if l>.82 else soft if brightness>.60 else accent if s>.18 else ink
    return re.sub(r'#[0-9a-fA-F]{6}\b',lambda m:mapped[m[0]],source)

def file_reference(text, extensions, required=True):
    text=str(text).strip().strip('"').strip("'")
    p=Path(os.path.expanduser(text)).resolve()
    if not text or not p.is_file():raise ValueError('Archivo no encontrado: '+text)
    if p.suffix.lower() not in extensions:raise ValueError('Formato no admitido: '+p.suffix)
    stat=p.stat()
    if stat.st_size==0:raise ValueError('Archivo vacío: '+p.name)
    # Hash only a bounded sample now. Full identity is frozen once in the ingest phase.
    with p.open('rb') as stream:
        first=stream.read(1024*1024);stream.seek(max(0,stat.st_size-1024*1024));last=stream.read(1024*1024)
    return {'path':str(p),'name':p.name,'bytes':stat.st_size,'mtime_ns':stat.st_mtime_ns,'sample_sha256':hashlib.sha256(first+last).hexdigest(),'full_sha256':'pendiente en ingesta; la muestra no es un hash completo'}

def prepare(data):
    title=str(data.get('title','')).strip();topic=str(data.get('topic','')).strip();audience=str(data.get('audience','')).strip()
    if not all((title,topic,audience)):raise ValueError('Completa nombre del lote, tema y público.')
    if any(len(x)>20000 for x in (title,topic,audience,str(data.get('script','')))):raise ValueError('Texto demasiado largo; adjunta el guion como archivo.')
    count=int(data.get('count',1));duration=int(data.get('duration',45))
    if not 1<=count<=30 or not 15<=duration<=90:raise ValueError('Elige 1–30 videos y 15–90 segundos de duración orientativa.')
    chosen=data.get('templates') or []
    allowed={t['id']:t for t in catalog()['templates']}
    if not chosen or len(set(chosen))!=len(chosen) or any(x not in allowed for x in chosen):raise ValueError('Elige una o más de las 30 plantillas, sin duplicados.')
    pal=selected_palette(data)
    paths=[p for p in str(data.get('masters','')).splitlines() if p.strip()]
    if not paths:raise ValueError('Indica la ruta de al menos un master.')
    if len(paths)>100:raise ValueError('Máximo 100 masters por lote.')
    masters=[file_reference(p,{'.mp4','.mov','.mkv','.webm','.m4v','.avi','.mts'}) for p in paths]
    if len({m['path'] for m in masters})!=len(masters):raise ValueError('Hay masters duplicados en la lista.')
    documents=[file_reference(p,{'.txt','.md','.pdf','.docx','.srt','.vtt','.json'}) for p in str(data.get('attachments','')).splitlines() if p.strip()]
    profile=data.get('profile','mac-auto' if os.name!='nt' else 'pc-a-gtx1660ti')
    if profile not in ('mac-auto','pc-a-gtx1660ti','pc-b-uhd620'):raise ValueError('Perfil inválido')
    slug=re.sub(r'[^a-z0-9]+','-',normalize(title)).strip('-')[:50] or 'lote'
    batch_id=time.strftime('%Y%m%d-%H%M%S')+'-'+slug+'-'+uuid.uuid4().hex[:6]
    base=ROOT/'proyecto/Nuevos-Videos';batch_root=ROOT/'proyecto/Lotes'/batch_id
    stage=ROOT/'runtime'/('preparar-'+uuid.uuid4().hex)
    stage.mkdir(parents=True)
    moved=[];committed=False
    try:
        with windows.machine_lock():
            records=rt.read(ROOT/'proyectos.json');start=max([30]+[int(x['video']) for x in records])+1
            if start+count-1>9999:raise ValueError('No quedan números disponibles.')
            hf=rt.config().get('hyperframes',rt.read(ROOT/'kit-config.json')['hyperframes'])
            ids=list(range(start,start+count));new=[]
            context={k:str(data.get(k,'')) for k in ('title','topic','audience','goal','tone','platform','cta','avoid','script','motion','brand','language','style_preference')}
            brief={**context,'batch_id':batch_id,'masters':masters,'attachments':documents,'palette':pal,'templates':chosen,'duration_target_s':duration,'videos':ids,'profile':profile,'flow':1,'hyperframes':hf,'template_assignment':'provisional; adaptar al contenido real tras ingesta','approved_for_render':False,'source_policy':'referencias sin copia; no mover los originales','created_at':rt.now()}
            lot=stage/'lote';(lot/'00-INGESTA').mkdir(parents=True)
            rt.save(lot/'CONTEXTO.json',brief)
            rt.save(lot/'MASTERS.json',{'files':masters,'policy':'No se han copiado ni movido los masters. Resolver nuevamente las rutas si cambian de equipo.'})
            (lot/'GUION.md').write_text(context['script'] or 'Guion adjunto o pendiente; transcribir la voz real antes de montar.',encoding='utf-8')
            prompt=(f'Lee AGENTS.md, ../INICIO_PARA_CODEX.md y Lotes/{batch_id}/CONTEXTO.json. Prepara el lote {title}. '
                f'Los masters y guiones están referenciados en ese contexto. Videos reservados: {ids}. '
                'Aplica flujo 1, las reglas vigentes, las 30 plantillas y la paleta elegida. La asignación por video es provisional hasta revisar la voz. '
                'Comprueba el diagnóstico del equipo. No instales ni descargues nada sin autorización explícita. '
                'Reutiliza una sola ingesta/ASR por master, guarda recibos de documentos realmente leídos, muestra propuesta y maqueta de fidelidad antes de montar. '
                'Conserva la identidad de cada plantilla; sugiere iconos, animaciones, zooms y recursos según el significado, protege rostro y gestos. '
                'Música/SFX, hook, subtítulos y QA siguen vigentes. No limpiar voz sin solicitud. '
                'No heredes aprobación de los videos anteriores. Solicita aprobación del candidato antes del render final; verifica el MP4 exacto. '
                'Comienza por revisar las fuentes y presenta los pasos y pendientes reales.')
            (lot/'ABRIR_EN_CODEX.txt').write_text(prompt,encoding='utf-8')
            (lot/'LEEME.md').write_text(f'# {title}\n\nAbre la carpeta `proyecto` en Codex y pega `ABRIR_EN_CODEX.txt`.\n\n'
                'Esta preparación reserva carpetas y guarda contexto; todavía no corta ni edita el master. '
                'Una sola ingesta se guarda en `00-INGESTA/`. No renombres ni muevas el master mientras lo uses. '
                'Puedes colocar futuros originales en la carpeta `entrada-masters/` de la entrega. '
                'Nombres sugeridos: `MASTER-01-tema.mp4`, `MASTER-02-tema.mov`, `GUION-01.md`; evita renombrar archivos ya referenciados.\n',encoding='utf-8')
            for idx,num in enumerate(ids):
                tid=chosen[idx%len(chosen)];p=stage/f'VIDEO-{num:02d}'
                dest=base/p.name
                if dest.exists():raise ValueError('La carpeta ya existe: '+str(dest))
                for d in ('source','editable/assets','editable/qa','entregas'):(p/d).mkdir(parents=True,exist_ok=True)
                item={'video':num,'path':f'Nuevos-Videos/{p.name}/editable','hyperframes':hf,'template':tid,'hook_end':None,'delivery_transfer':'bt709','sfx_plan_present':False,'windows_runtime_verified':False,'batch':batch_id,'profile':profile}
                new.append(item);rt.save(p/'windows-project.json',item)
                rt.save(p/'CONTEXTO_LOTE.json',{'context':'../../Lotes/'+batch_id+'/CONTEXTO.json','masters':'../../Lotes/'+batch_id+'/MASTERS.json','assignment':'provisional'})
                rt.save(p/'PLANTILLA_SELECCIONADA.json',{'selection':allowed[tid],'palette':pal,'code_reference':f'plantillas-codigo/{tid}','new_video_approved':False,'flow':1,'stage':'prepared_not_composed'})
                rt.save(p/'PALETA.json',pal)
                tokens=':root {\n'+''.join(f'  --{k}: {v};\n' for k,v in zip(pal['roles'],pal['colors']))+'}\n'
                (p/'editable/assets/paleta.css').write_text(tokens,encoding='utf-8')
                # Offline board: paths relative to the new video, not the server or old machine.
                svg=board(tid,pal).replace('/assets/','../../Serie-IA-Negocios-10-Videos/PROPUESTAS-ESTRUCTURA/assets-compartidos/')
                (p/'VISTA_PLANTILLA.svg').write_text(svg,encoding='utf-8')
                shutil.copy2(ROOT/'proyecto/Framework-Edicion-Social/templates/template-fidelity-review.md',p/'QA_FIDELIDAD_PLANTILLA.md')
                (p/'LEEME.md').write_text(f'# {p.name}\n\nContexto: ../../Lotes/{batch_id}/CONTEXTO.json\n\nPlantilla {tid}; paleta {pal["name"]}. Asignación provisional. '
                    'Consultar instrucciones y crear recibo de inicio al comenzar. La vista es cromática y estática; no es una nueva maqueta adaptada a tu voz ni un render aprobado.\n',encoding='utf-8')
            base.mkdir(parents=True,exist_ok=True);batch_root.parent.mkdir(parents=True,exist_ok=True)
            lot.rename(batch_root);moved.append(batch_root)
            for num in ids:
                dest=base/f'VIDEO-{num:02d}';(stage/dest.name).rename(dest);moved.append(dest)
            # Commit registry only after every file is ready. Roll back new folders on failure.
            tmp=ROOT/'proyectos.next.json';rt.save(tmp,records+new);tmp.replace(ROOT/'proyectos.json');committed=True
        warnings=[]
        try:
            with windows.machine_lock():
                history=ROOT/'asistente/historial-paletas.json';old=rt.read(history) if history.exists() else []
                rt.save(history,old+[{'batch':batch_id,'palette':pal['id'],'colors':pal['colors'],'at':rt.now()}])
                day=rt.now()[:10]
                entry=(f'\n\n### {day} — Lote preparado con el asistente: {batch_id}\n\n'
                    f'- Petición: preparar {count} videos sobre {topic}; público: {audience}.\n'
                    '- Punto de partida: fuentes indicadas por el usuario, todavía sin ingesta ni montaje.\n'
                    f'- Cambios y archivos: Lotes/{batch_id}/, VIDEO-{start:02d} a VIDEO-{ids[-1]:02d}; contexto, masters referenciados, selección provisional {chosen}, paleta {pal["name"]}, tablero, QA y carpetas.\n'
                    '- Motivo: comenzar con contexto y recursos explícitos, sin duplicar originales.\n'
                    '- Validación: rutas existentes, ausencia de sobrescritura y contraste de tinta/papel; no se ha analizado la voz ni comprobado el contenido audiovisual.\n'
                    '- Resultado: preparado, sin composición ni aprobación de render.\n'
                    '- Aprendizaje: reservar carpetas no sustituye el recibo de inicio ni la fidelidad adaptada a la voz.\n'
                    '- Pendiente: diagnóstico del equipo, ingesta/ASR reutilizable, recibo de documentos leídos, propuesta, fidelidad, montaje, QA exacto y aprobación.\n')
                memory=ROOT/'proyecto/BITACORA_CURSO_EDICION.md'
                previous=memory.read_text(encoding='utf-8') if memory.exists() else '# Bitácora de esta entrega\n\nÚltima actualización: '+day+'.\n'
                previous=re.sub(r'Última actualización: [^\n]+',f'Última actualización: {day}.',previous,count=1)
                memory.write_text(previous+entry,encoding='utf-8')
                changes=ROOT/'proyecto/Lotes/CHANGELOG.md'
                previous=changes.read_text(encoding='utf-8') if changes.exists() else '# Historial de preparación de lotes\n'
                changes.write_text(previous+entry,encoding='utf-8')
        except Exception as e:
            warnings.append('Lote creado; falta completar historial/bitácora: '+str(e))
        return {'batch':batch_id,'folder':str(batch_root),'workspace':str(ROOT/'proyecto'),'prompt':prompt,'videos':ids,'status':'prepared_not_composed','warnings':warnings}
    except Exception:
        if not committed:
            for p in reversed(moved):shutil.rmtree(p)
        raise
    finally:shutil.rmtree(stage,ignore_errors=True)
