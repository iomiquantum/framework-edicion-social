'use strict';
// Shared folder persistence for the guide and wizard. Acknowledgements mean disk writes,
// not just queued requests or browser storage. One revision per document prevents clobbers.
class FolderProgress {
  constructor(kind, onStatus) {
    this.kind=kind;this.onStatus=onStatus;this.token=location.hash.slice(1);this.revision=0;this.loaded=false;
    this.latest=null;this.sending=false;this.timer=null;this.failed=false;
  }
  async request(method,data) {
    const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),10000);
    try {
      const response=await fetch('/api/progress/'+this.kind,{method,headers:{'X-Setup-Token':this.token,'Content-Type':'application/json'},body:data===undefined?undefined:JSON.stringify(data),signal:controller.signal});
      const result=await response.json();
      if(!response.ok)throw Error(result.error||'No se pudo guardar.');
      return result;
    } catch(e) {
      if(e instanceof TypeError||e.name==='AbortError')throw Error('Se perdió la conexión con el asistente. Abre INICIO de nuevo; conserva esta ventana y descarga tu progreso si hay cambios sin guardar.');
      throw e;
    } finally {clearTimeout(timeout);}
  }
  async load() {
    this.onStatus('loading','Leyendo el progreso de esta carpeta…');
    try {
      const result=await this.request('GET');this.revision=result.revision;this.loaded=true;this.failed=false;
      this.onStatus(result.warning?'warning':'saved',result.warning||'Guardado en MI-PROGRESO · listo para continuar.');return result.data;
    } catch(e) {this.failed=true;this.onStatus('error',e.message);throw e;}
  }
  queue(data) {
    if(!this.loaded){this.onStatus('error','No se ha recuperado el progreso anterior. Reintenta antes de modificarlo.');return;}
    this.latest=JSON.parse(JSON.stringify(data));this.onStatus('saving','Guardando en esta carpeta…');
    clearTimeout(this.timer);this.timer=setTimeout(()=>this.flush(),220);
  }
  async flush() {
    clearTimeout(this.timer);
    if(this.sending||!this.loaded)return false;
    this.sending=true;this.failed=false;
    try {
      while(this.latest) {
        const snapshot=this.latest;this.latest=null;
        try {
          const result=await this.request('POST',{revision:this.revision,data:snapshot});
          this.revision=result.revision;
        } catch(e) {if(!this.latest)this.latest=snapshot;throw e;}
      }
      this.onStatus('saved','Guardado en MI-PROGRESO · '+new Date().toLocaleTimeString('es',{hour:'2-digit',minute:'2-digit',second:'2-digit'}));return true;
    } catch(e) {this.failed=true;this.onStatus('error',e.message);return false;}
    finally {this.sending=false;}
  }
  get dirty(){return Boolean(this.latest||this.sending);}
}
