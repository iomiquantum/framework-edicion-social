import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
import asistente
import progreso as p


def guide():
    return {'schema':'framework.guia.progreso','version':1,'activeOS':'windows','paths':{
        os:{'step':'welcome','checks':{},'notes':{},'updatedAt':None} for os in ('windows','mac')}}


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='alumno con ñ ')
        self.root=Path(self.tmp.name);self.patch=patch.object(p,'ROOT',self.root);self.patch.start()
    def tearDown(self):self.patch.stop();self.tmp.cleanup()
    def test_roundtrip_and_previous_revision(self):
        d=guide();p.write('guia',d,0)
        d['paths']['windows']['notes']['welcome']='Retomar mañana';p.write('guia',d,1)
        self.assertEqual(p.read('guia')['data'],d)
        old=json.loads((self.root/'MI-PROGRESO/guia.anterior.json').read_text())
        self.assertEqual(old['revision'],1)
        self.assertNotIn('welcome',old['data']['paths']['windows']['notes'])
    def test_two_windows_cannot_silently_overwrite(self):
        p.write('guia',guide(),0)
        with self.assertRaises(p.Conflict):p.write('guia',guide(),0)
        self.assertEqual(p.read('guia')['revision'],1)
    def test_corrupt_current_recovers_previous(self):
        p.write('guia',guide(),0);p.write('guia',guide(),1)
        path=self.root/'MI-PROGRESO/guia.json';path.write_text('{broken')
        recovered=p.read('guia');self.assertIn('warning',recovered)
        p.write('guia',guide(),recovered['revision'])
        self.assertEqual(p.read('guia')['revision'],2)
    def test_corrupt_both_preserved_for_help(self):
        p.write('guia',guide(),0)
        path=self.root/'MI-PROGRESO/guia.json';path.write_text('{broken')
        with self.assertRaises(ValueError):p.write('guia',guide(),1)
        self.assertEqual(path.read_text(),'{broken')
    def test_explicit_backup_is_importable_and_does_not_replace_work(self):
        d=guide();result=p.backup('guia',d)
        self.assertEqual(json.loads(Path(result['path']).read_text()),d)
        self.assertEqual(p.read('guia')['revision'],0)
        self.assertEqual(p.copies(),[Path(result['path']).name])
        self.assertEqual(p.copies(Path(result['path']).name),d)
        with self.assertRaises(ValueError):p.copies('../../guia.json')
    def test_unknown_paths_rejected(self):
        for name in ['../outside','guia/../../outside','runtime']:
            with self.assertRaises(ValueError):p.read(name)
        self.assertFalse((self.root/'outside').exists())
    def test_invalid_checkboxes_do_not_replace_valid_state(self):
        p.write('guia',guide(),0);bad=guide();bad['paths']['windows']['checks']['welcome']=['true',True]
        with self.assertRaises(ValueError):p.write('guia',bad,1)
        self.assertEqual(p.read('guia')['revision'],1)
    def test_windows_mac_and_recording_steps_are_independent(self):
        d=guide();d['paths']['windows']['checks']['recording']=[True,True];p.write('guia',d,0)
        self.assertEqual(p.read('guia')['data']['paths']['mac']['checks'],{})
        self.assertEqual(len(p.STEP_COUNTS),15)
    def test_recording_script_and_checklist_roundtrip(self):
        d={'video':31,'take':2,'case':'correction','hook':'¿Qué harás hoy?','body':'<script>literal</script>','close':'Gracias','notes':'Ejemplo','checks':[True,False,False,False,False,False]}
        p.write('grabacion',d,0);self.assertEqual(p.read('grabacion')['data'],d)
    def test_bad_recording_numbers_and_case_rejected(self):
        for data in [{'video':True},{'take':0},{'case':'execute'},{'checks':[True]}]:
            with self.assertRaises(ValueError):p.write('grabacion',data,0)
    def test_draft_stores_text_palette_templates_and_step(self):
        d={'topic':'Árboles','templates':['T01','T30'],'colors':['#112233','#ffffff','#aabbcc','#000000'],'palette':'bosque','step':3}
        p.write('borrador',d,0);saved=p.read('borrador')['data']
        for key in d:self.assertEqual(saved[key],d[key])
    def test_failed_atomic_replace_keeps_current_and_removes_temp(self):
        p.write('guia',guide(),0)
        with patch.object(p.os,'replace',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):p.write('guia',guide(),1)
        self.assertEqual(p.read('guia')['revision'],1)
        self.assertEqual(list((self.root/'MI-PROGRESO').glob('*.tmp')),[])


class ProgressHTTPTests(unittest.TestCase):
    setUp=ProgressTests.setUp
    tearDown=ProgressTests.tearDown
    @classmethod
    def setUpClass(cls):
        cls.server=asistente.http.server.ThreadingHTTPServer(('127.0.0.1',0),asistente.Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close()
    def call(self,path,method='GET',data=None,token=True,origin=None):
        headers={'Content-Type':'application/json'}
        if token:headers['X-Setup-Token']=asistente.TOKEN
        if origin:headers['Origin']=origin
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        c.request(method,path,json.dumps(data) if data is not None else None,headers)
        r=c.getresponse();body=r.read();status=r.status;c.close();return status,body
    def test_api_roundtrip_conflict_and_authentication(self):
        payload={'revision':0,'data':guide()}
        self.assertEqual(self.call('/api/progress/guia','POST',payload,token=False)[0],403)
        self.assertEqual(self.call('/api/progress/guia','POST',payload,origin='https://example.com')[0],403)
        self.assertEqual(self.call('/api/progress/guia','POST',payload)[0],200)
        self.assertEqual(self.call('/api/progress/guia','POST',payload)[0],409)
        status,raw=self.call('/api/progress/guia');self.assertEqual(status,200)
        self.assertEqual(json.loads(raw)['data'],guide())
    def test_api_cannot_write_last_lot_or_arbitrary_file(self):
        self.assertEqual(self.call('/api/progress/ultimo-lote','POST',{'revision':0,'data':{}})[0],404)
        self.assertNotEqual(self.call('/api/progress/../../secrets')[0],200)
    def test_pages_and_shared_script_are_served(self):
        for path in ['/guia','/grabacion','/asistente/progreso.js']:
            status,raw=self.call(path);self.assertEqual(status,200);self.assertGreater(len(raw),100)
        self.assertNotEqual(self.call('/MI-PROGRESO/guia.json')[0],200)
    def test_backup_api_can_restore_without_browser_file_dialog(self):
        status,raw=self.call('/api/progress-backup','POST',{'kind':'guia','data':guide()})
        self.assertEqual(status,200);name=Path(json.loads(raw)['path']).name
        self.assertEqual(json.loads(self.call('/api/progress-copies')[1]),[name])
        self.assertEqual(json.loads(self.call('/api/progress-copy?name='+name)[1]),guide())


if __name__=='__main__':unittest.main()
