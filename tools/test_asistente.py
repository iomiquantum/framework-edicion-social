import contextlib, http.client, json, os, shutil, struct, tempfile, threading, time, unittest, xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch
import asistente as app
import onboarding as ob
import runtime_setup as rt
import windows

class PaletteTests(unittest.TestCase):
    def test_five_distinct_palettes_and_readable_pairs(self):
        result=ob.suggestions('marketing y educación de tecnología')
        self.assertEqual(len(result),5);self.assertEqual(len({p['id'] for p in result}),5)
        for p in ob.PALETTES:self.assertGreaterEqual(ob.contrast(p[2][0],p[2][1]),4.5)
    def test_bad_colors_block_creation(self):
        for colors in [['#123']*4,['red']*4,['#ffffff']*4]:
            with self.assertRaises(ValueError):ob.selected_palette({'palette':'bosque','colors':colors})
    def test_unchanged_palette_keeps_identity_for_history(self):
        p=ob.palette('bosque');self.assertEqual(ob.selected_palette({'palette':'bosque','colors':p['colors']})['id'],'bosque')
    def test_all_boards_preserve_nodes_and_embedded_photos(self):
        base=(ob.ROOT/rt.read(ob.ROOT/'kit-config.json')['templates']).parent
        for t in ob.catalog()['templates']:
            original=(base/t['artifact']).with_suffix('.svg').read_text();before=ET.fromstring(original)
            result=ob.board(t['id'],ob.palette('oceano'),embed=True);after=ET.fromstring(result)
            self.assertEqual([n.tag for n in before.iter()],[n.tag for n in after.iter()],t['id'])
            self.assertNotIn('/assets/',result);self.assertNotIn('../assets-compartidos/',result)
            if '<image ' in original:self.assertIn('data:image/',result)
            width,height=struct.unpack('>II',(base/t['artifact']).read_bytes()[16:24]);self.assertEqual(after.attrib['viewBox'],f'0 0 {width} {height}')
    def test_unknown_template_blocked(self):
        with self.assertRaises(ValueError):ob.board('../../etc/passwd')

class BatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='estudio con ñ ');self.root=Path(self.tmp.name)
        self.original=ob.ROOT
        self.stack=contextlib.ExitStack()
        for module in (ob,rt,windows):self.stack.enter_context(patch.object(module,'ROOT',self.root))
        rt.save(self.root/'kit-config.json',{'templates':'catalog.json','hyperframes':'0.8.102'})
        rt.save(self.root/'catalog.json',{'templates':[{'id':'T01','name':'Uno','artifact':'unused.png'},{'id':'T02','name':'Dos','artifact':'unused2.png'}]})
        rt.save(self.root/'proyectos.json',[])
        f=self.root/'proyecto/Framework-Edicion-Social/templates/template-fidelity-review.md';f.parent.mkdir(parents=True);f.write_text('Pendiente')
        self.master=self.root/'master con ñ.mp4';self.master.write_bytes(b'test synthetic media placeholder')
        self.data={'title':'../Lote <script>','topic':'IA','audience':'Personas','templates':['T01','T02'],'palette':'bosque','masters':str(self.master),'count':2,'duration':45,'profile':'mac-auto'}
        self.stack.enter_context(patch.object(ob,'board',return_value='<svg xmlns="http://www.w3.org/2000/svg"/>'))
    def tearDown(self):self.stack.close();self.tmp.cleanup()
    def test_prepares_shared_master_no_copy_no_approval(self):
        before=self.master.read_bytes();result=ob.prepare(self.data)
        self.assertEqual(result['videos'],[31,32]);self.assertEqual(self.master.read_bytes(),before)
        self.assertTrue(Path(result['folder']).is_relative_to(self.root/'proyecto/Lotes'))
        for n,tid in [(31,'T01'),(32,'T02')]:
            item,path=windows.project(n);self.assertEqual(item['template'],tid)
            self.assertFalse((path/'index.html').exists());self.assertEqual(list((path.parent/'source').iterdir()),[])
            self.assertFalse(rt.read(path.parent/'PLANTILLA_SELECCIONADA.json')['new_video_approved'])
        self.assertTrue((Path(result['folder'])/'00-INGESTA').is_dir())
        result2=ob.prepare(self.data);self.assertEqual(result2['videos'],[33,34])
    def test_missing_master_makes_no_project(self):
        with self.assertRaises(ValueError):ob.prepare({**self.data,'masters':'/not/a/real/master.mp4'})
        self.assertEqual(rt.read(self.root/'proyectos.json'),[])
    def test_duplicate_master_blocked(self):
        with self.assertRaises(ValueError):ob.prepare({**self.data,'masters':str(self.master)+'\n'+str(self.master)})
    def test_existing_folder_is_not_overwritten(self):
        p=self.root/'proyecto/Nuevos-Videos/VIDEO-31';p.mkdir(parents=True);(p/'keep').write_text('keep')
        with self.assertRaises(ValueError):ob.prepare(self.data)
        self.assertEqual((p/'keep').read_text(),'keep');self.assertEqual(rt.read(self.root/'proyectos.json'),[])
    def test_failed_build_does_not_commit_partial_registry(self):
        with patch.object(shutil,'copy2',side_effect=OSError('test failure')):
            with self.assertRaises(OSError):ob.prepare(self.data)
        self.assertEqual(rt.read(self.root/'proyectos.json'),[])
        self.assertFalse((self.root/'proyecto/Nuevos-Videos/VIDEO-31').exists())
    def test_readable_palette_history_avoids_recent(self):
        ob.prepare(self.data);self.assertNotIn('bosque',[x['id'] for x in ob.suggestions('bienestar confianza')])

class SetupTests(unittest.TestCase):
    def test_install_without_consent_never_runs(self):
        with patch.object(rt,'run') as run:
            with self.assertRaises(PermissionError):rt.perform({'kind':'node'})
            run.assert_not_called()
    def test_expired_plan_never_runs(self):
        with patch.object(rt,'run') as run:
            with self.assertRaises(ValueError):rt.perform({'kind':'node','created_at':time.time()-700},authorized=True)
            run.assert_not_called()
    def test_missing_latest_release_does_not_install_guessed_version(self):
        with self.assertRaises(ValueError):rt.installation_plan('node',{'releases':{'node':{'version':None}}})
    def test_no_network_returns_explicit_unknown_versions(self):
        with patch.object(rt,'request',side_effect=OSError('offline')):
            result=rt.latest()
            self.assertTrue(all(v['version'] is None and 'error' in v for v in result['releases'].values()))
    def test_doctor_payload_false_is_not_success(self):
        with patch.object(rt,'hf_command',return_value=(['hyperframes'],'0.0.1')),patch.object(rt,'run',return_value='{"ok":false}'),patch.object(rt,'save'),patch.object(rt,'hardware',return_value={}):
            d=rt.diagnose();self.assertFalse(d['dependencies_ok'])
            self.assertFalse(next(x['ok'] for x in d['checks'] if x['name']=='HyperFrames y Chrome'))

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=app.http.server.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close()
    def call(self,path,method='GET',data=None,headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port);h=headers or {};h['Content-Type']='application/json'
        c.request(method,path,json.dumps(data or {}) if method=='POST' else None,h);r=c.getresponse();body=r.read();status=r.status;c.close();return status,body
    def test_no_token_and_cross_origin_cannot_mutate(self):
        self.assertEqual(self.call('/api/prepare','POST',{})[0],403)
        self.assertEqual(self.call('/api/prepare','POST',{}, {'X-Setup-Token':app.TOKEN,'Origin':'https://untrusted.example'})[0],403)
    def test_token_needed_for_local_paths(self):self.assertEqual(self.call('/api/info')[0],403)
    def test_arbitrary_files_are_not_served(self):self.assertNotEqual(self.call('/assets/../../kit-config.json')[0],200)
    def test_no_ready_without_real_checks(self):
        status,raw=self.call('/api/ready','POST',{'codex_signed_in':True},{'X-Setup-Token':app.TOKEN})
        self.assertEqual(status,200);self.assertFalse(json.loads(raw)['ready'])
    def test_catalog_access_and_five_suggestions(self):
        status,raw=self.call('/api/palettes','POST',{'context':'educacion'},{'X-Setup-Token':app.TOKEN})
        self.assertEqual(status,200);self.assertEqual(len(json.loads(raw)),5)

if __name__=='__main__':unittest.main()
