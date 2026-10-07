"""Read-only frozen audit of exported videos; no new renders or ASR."""
from pathlib import Path
from html.parser import HTMLParser
import json, re, hashlib, subprocess, time
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

out=Path(__file__).resolve().parent; root=out.parents[2]; series=root/'Serie-IA-Negocios-10-Videos'
ff='/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg'; fp='/opt/homebrew/opt/ffmpeg-full/bin/ffprobe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Cues(HTMLParser):
    def __init__(self): super().__init__(); self.depth=0;self.cue=None;self.rows=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='div':
            self.depth+=1
            if self.cue is None and set(a.get('class','').split())&{'cue','caption'}:
                self.cue={'id':a.get('id'),'attrs':a,'depth':self.depth,'parts':[]}
        if self.cue and tag in ['br']:self.cue['parts'].append(' ')
        if self.cue and tag in ['span','b','strong','em']:self.cue['parts'].append(' ')
    def handle_data(self,data):
        if self.cue:self.cue['parts'].append(data)
    def handle_endtag(self,tag):
        if self.cue and tag in ['span','b','strong','em']:self.cue['parts'].append(' ')
        if tag=='div':
            if self.cue and self.cue['depth']==self.depth:
                c=self.cue;c['text']=' '.join(''.join(c.pop('parts')).split());self.rows.append(c);self.cue=None
            self.depth-=1
def command(label,args):
    start=time.monotonic();r=subprocess.run(args,capture_output=True,text=True,stdin=subprocess.DEVNULL)
    assert r.returncode==0,r.stderr[-1200:]
    return r.stdout,{'label':label,'argv':args,'wall_s':time.monotonic()-start,'exit_code':r.returncode}
rows=[];commands=[]
for n in list(range(1,17))+[21,22]:
    v=series/f'VIDEO-{n:02d}';p=v/('editable-image-v4' if n==16 else f'editable-hyperframes-video-{n:02d}')
    if n==1: video=v/'deliveries/VIDEO-01-instagram-reels.mp4';selection='Instagram delivery file; no approval inferred from filename.'
    elif n<=10:
        candidates=list(v.glob(f'VIDEO-{n:02d}_REVISION_v*.mp4'))
        video=max(candidates,key=lambda x:int(re.search(r'_v(\d+)',x.name).group(1)));selection='Highest numbered root revision at inventory time; approval not inferred.'
    elif n<=15:video=p/f'renders/VIDEO-{n:02d}-FINAL.mp4';selection='Current FINAL filename frozen by hash; approval not inferred.'
    elif n==16: video=v/'VIDEO-16-PARA-APROBACION-v4.mp4';selection='Explicit user approval receipt for v4.'
    else:
        receipt=json.loads((v/'ENTREGA.json').read_text()); a=receipt['artifact']
        path=a if isinstance(a,str) else a.get('path',a.get('file'))
        video=Path(path) if Path(path).is_absolute() else v/path
        if not video.exists():video=root/path
        assert sha(video)==receipt['sha256'];selection='ENTREGA.json artifact at inventory time; later concurrent revisions not covered.'
    assert video.exists(),video
    hashed=sha(video);raw,cmd=command(f'probe{n}',[fp,'-v','error','-show_streams','-show_format','-of','json',str(video)]);commands.append(cmd)
    probe=json.loads(raw);stream=next(s for s in probe['streams'] if s['codec_type']=='video');duration=float(stream['duration']);fps=float(stream['avg_frame_rate'].split('/')[0])/float(stream['avg_frame_rate'].split('/')[1])
    cpath=p/'compositions/captions-es.html';text=cpath.read_text();index=(p/'index.html').read_text();parser=Cues();parser.feed(text)
    timing={id:(float(a),float(b)) for id,a,b in re.findall(r'\["#([^"\]]+)",\s*([\d.]+),\s*([\d.]+)\]',text)}
    if n==21:
        cr=json.loads((p/'captions.json').read_text());timing.update({f'cue-{i}':(r['start'],r['end']) for i,r in enumerate(cr)})
    cue_rows=[]
    for c in parser.rows:
        a=c['attrs'];t=timing.get(c['id'])
        if t is None and 'data-start' in a and 'data-duration' in a:t=(float(a['data-start']),float(a['data-start'])+float(a['data-duration']))
        if t:
            plain=c['text'];d=t[1]-t[0]
            cue_rows.append({'id':c['id'],'text':plain,'start_s':t[0],'end_s':t[1],'duration_s':d,'cps_including_spaces':len(plain)/d,'wpm':len(plain.split())/d*60})
    assert cue_rows,n
    css='\n'.join(re.findall(r'<style>(.*?)</style>',text+'\n'+index,re.S)); styles=[{'selector':a.strip(),'declarations':b.strip()} for a,b in re.findall(r'([^{}]+)\{([^{}]+)\}',css) if re.search(r'cue|caption',a) and any(k in b for k in ['font-size','top:','bottom:'])]
    # Review first, middle and longest caption. Unique frames; add last cue if long is already present.
    specs=[cue_rows[0],cue_rows[len(cue_rows)//2],max(cue_rows,key=lambda c:len(c['text']))]
    indices=sorted(set(min(int((c['start_s']+c['end_s'])/2*fps),int(duration*fps)-1) for c in specs))
    if len(indices)<3:indices=sorted(set(indices+[int((cue_rows[-1]['start_s']+cue_rows[-1]['end_s'])/2*fps)]))
    folder=out/f'VIDEO-{n:02d}';folder.mkdir(exist_ok=False)
    is_hdr=stream.get('color_transfer') in ['arib-std-b67','smpte2084']
    tone=',zscale=t=linear:npl=100,format=gbrpf32le,tonemap=hable:desat=0,zscale=p=bt709:t=bt709:m=bt709:r=tv' if is_hdr else ''
    select='+'.join(f'eq(n\\,{x})' for x in indices)
    _,cmd=command(f'frames{n}',[ff,'-nostdin','-v','error','-i',str(video),'-an','-vf',f'select={select}'+tone+',scale=360:640,format=rgb24','-fps_mode','vfr','-frames:v',str(len(indices)),'-start_number','0',str(folder/'frame-%02d.png')]);commands.append(cmd)
    files=sorted(folder.glob('frame-*.png'));assert len(files)==len(indices)
    sheet=Image.new('RGB',(1100,704),'#f4f1e8');draw=ImageDraw.Draw(sheet)
    draw.text((12,10),f'VIDEO-{n:02d} | {video.name} | '+('HDR mapped to SDR' if is_hdr else 'SDR'),fill='#17252c')
    for i,(f,ind) in enumerate(zip(files,indices)):
        sheet.paste(Image.open(f),(i*368,36));draw.text((i*368+12,681),f'frame {ind} / {ind/fps:.3f}s',fill='#17252c')
    sheet.save(folder/'contact-sheet.png')
    assert sha(video)==hashed
    rows.append({'video_id':f'VIDEO-{n:02d}','file':str(video),'sha256':hashed,'bytes':video.stat().st_size,'selection':selection,'metadata':{'duration_s':duration,'width':stream['width'],'height':stream['height'],'fps':fps,'color_transfer':stream.get('color_transfer'),'viewing_conversion':'HLG/PQ to BT709 Hable, not certified HDR' if is_hdr else 'SDR BT709 decoded'},'caption_source':{'path':str(cpath),'sha256':sha(cpath),'binding_limit':'Current editable inspected separately; exact historical render source equality not claimed without receipt.'},'caption_css':styles,'cue_count':len(cue_rows),'cues':cue_rows,'max_cps':max(c['cps_including_spaces'] for c in cue_rows),'over20cps':sum(c['cps_including_spaces']>20 for c in cue_rows),'mobile_font_scale':'At360px video width, 1080px source fonts scale by1/3.','review_frames':[{'path':str(f),'sha256':sha(f),'frame_index':ind,'time_s':ind/fps} for f,ind in zip(files,indices)],'contact_sheet':str(folder/'contact-sheet.png'),'visual_review_completed':False})
    print(json.dumps({'video':n,'cues':len(cue_rows),'max_cps':round(rows[-1]['max_cps'],1),'over20':rows[-1]['over20cps'],'frames':len(files)},ensure_ascii=False),flush=True)
(out/'export-audit.json').write_text(json.dumps({'created_at_utc':datetime.now(timezone.utc).isoformat(),'status':'technical_extraction_complete_visual_review_pending','scope':'18 distinct short-video exports; three selected caption states each, not every scene/frame or listening. Approved outputs untouched.','videos':rows,'commands':commands},ensure_ascii=False,indent=2)+'\n')
