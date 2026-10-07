import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

import portable_fcntl as locks
import windows


class PortableKitTests(unittest.TestCase):
    def test_real_process_exclusion_and_release(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'process.lock'
            child = "import portable_fcntl as f,sys; h=open(sys.argv[1],'a+b'); f.flock(h,f.LOCK_EX|f.LOCK_NB)"
            env = {**os.environ, 'PYTHONPATH':str(Path(__file__).parent)}
            with path.open('a+b') as handle:
                locks.flock(handle, locks.LOCK_EX)
                blocked = subprocess.run([sys.executable,'-c',child,str(path)],env=env,capture_output=True)
                self.assertNotEqual(blocked.returncode,0)
                locks.flock(handle, locks.LOCK_UN)
                free = subprocess.run([sys.executable,'-c',child,str(path)],env=env,capture_output=True)
                self.assertEqual(free.returncode,0,free.stderr)

    def test_windows_branch_restores_position_and_unlocks(self):
        with tempfile.TemporaryFile() as handle:
            handle.write(b'abcdef'); handle.flush(); handle.seek(3)
            calls=[]
            m=types.SimpleNamespace(LK_NBLCK=2,LK_UNLCK=0,locking=lambda fd, op, n:calls.append((op,n,os.lseek(fd,0,os.SEEK_CUR))))
            with patch.object(locks.os,'name','nt'),patch.dict(sys.modules,msvcrt=m):
                locks.flock(handle,locks.LOCK_SH)
                self.assertEqual(handle.tell(),3)
                locks.flock(handle,locks.LOCK_UN)
            self.assertEqual(calls,[(2,1,0),(0,1,0)])

    def test_windows_branch_nonblocking_conflict(self):
        def conflict(*args): raise OSError(errno.EACCES,'locked')
        m=types.SimpleNamespace(LK_NBLCK=2,LK_UNLCK=0,locking=conflict)
        with tempfile.TemporaryFile() as handle:
            with patch.object(locks.os,'name','nt'),patch.dict(sys.modules,msvcrt=m):
                with self.assertRaises(BlockingIOError):locks.flock(handle,locks.LOCK_EX|locks.LOCK_NB)

    def test_manifest_cannot_redirect_to_mac_or_parent(self):
        with patch.object(windows,'read',return_value=[{'video':30,'path':'../../source-mac'}]):
            with self.assertRaisesRegex(ValueError,'outside'):windows.project(30)

    def test_missing_sfx_plan_blocks_before_mix(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(windows,'execute') as run:
                with self.assertRaisesRegex(RuntimeError,'SFX plan'):
                    windows.preflight({'hook_end':None},Path(folder),{'ffmpeg':'ffmpeg','ffprobe':'ffprobe'},Path(folder)/'qa')
                self.assertEqual(run.call_count,1) # Visible-text guard runs; no guessed audio plan.

    def test_copy_receipt_keeps_distinct_source_and_adapted_hashes(self):
        m=windows.read(windows.ROOT/'evidencia/manifiesto-copia.json')
        changed={r['path'] for r in m['files'] if r.get('source_sha256') and r['source_sha256']!=r['snapshot_sha256']}
        self.assertEqual(changed,{r['path'] for r in m['adaptations']})
        self.assertTrue(changed)

    def make_empty_kit(self, folder):
        root=Path(folder)
        windows.save(root/'kit-config.json',{'hyperframes':'0.8.102','templates':'catalog.json'})
        windows.save(root/'catalog.json',{'templates':[{'id':'T05','name':'Comic pop','status':'approved'}]})
        windows.save(root/'proyectos.json',[])
        path=root/'proyecto/Framework-Edicion-Social/templates/template-fidelity-review.md'
        path.parent.mkdir(parents=True);path.write_text('Fidelity review: pending')
        return root

    def test_new_video_uses_design_without_inheriting_old_media_or_approval(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.make_empty_kit(folder)
            with patch.object(windows,'ROOT',root):
                windows.new_project(31,'T05')
                item,path=windows.project(31)
                self.assertEqual(item['template'],'T05')
                self.assertIsNone(item['hook_end'])
                self.assertFalse((path/'index.html').exists())
                self.assertEqual(list((path.parent/'source').iterdir()),[])
                selection=windows.read(path.parent/'PLANTILLA_SELECCIONADA.json')
                self.assertFalse(selection['new_video_approved'])
                self.assertEqual(selection['flow'],1)
                registry=(root/'proyectos.json').read_bytes()
                with self.assertRaisesRegex(ValueError,'already exists'):windows.new_project(31,'T05')
                self.assertEqual((root/'proyectos.json').read_bytes(),registry)

    def test_unknown_template_cannot_create_project(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.make_empty_kit(folder)
            with patch.object(windows,'ROOT',root):
                with self.assertRaises(ValueError):windows.new_project(32,'T99')
                self.assertFalse((root/'proyecto/Nuevos-Videos').exists())

    def test_invalid_hook_does_not_pass_project_loading(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.make_empty_kit(folder)
            with patch.object(windows,'ROOT',root):
                windows.new_project(31,'T05')
                path=root/'proyecto/Nuevos-Videos/VIDEO-31/windows-project.json'
                data=windows.read(path);data['hook_end']=-1;windows.save(path,data)
                with self.assertRaisesRegex(ValueError,'hook_end'):windows.project(31)


if __name__=='__main__':unittest.main()
