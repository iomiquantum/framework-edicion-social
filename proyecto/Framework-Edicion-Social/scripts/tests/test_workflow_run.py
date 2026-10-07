import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import shutil

spec=importlib.util.spec_from_file_location('workflow_run',Path(__file__).resolve().parents[1]/'workflow_run.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class WorkflowRunTests(unittest.TestCase):
    def test_default_and_explicit_selection_keep_safety_floor(self):
        with tempfile.TemporaryDirectory() as temp:
            for flow in (1,2,3):
                run=Path(temp)/str(flow)
                d=module.init(run,'VIDEO-26',flow)
                self.assertTrue(d['profile']['safety_floor_required'])
                self.assertTrue(d['profile']['exact_export_qa_required'])
                self.assertEqual(len(d['profile']['qa_passes']),3)
                self.assertEqual(d['approval_status'],'not_inferred')
            d=module.init(Path(temp)/'default','VIDEO-27')
            self.assertEqual(d['profile']['profile_id'],'flujo-1')

    def test_existing_run_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            run=Path(temp)/'run';module.init(run,'VIDEO-26')
            before=(run/'run.json').read_bytes()
            with self.assertRaises(ValueError):module.init(run,'VIDEO-26',2)
            self.assertEqual((run/'run.json').read_bytes(),before)

    def test_events_are_unique_and_changed_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            run=Path(temp)/'run';module.init(run,'VIDEO-26',2)
            evidence=Path(temp)/'check.json';evidence.write_text('{"ok":true}')
            first=module.event(run,'full_check','stable candidate',evidence)
            second=module.event(run,'full_check','after correction',evidence)
            self.assertNotEqual(first['event_id'],second['event_id'])
            report=module.report(run,[evidence])
            self.assertEqual(report['event_counts']['full_check'],2)
            self.assertEqual(report['qa_status'],'not_evaluated_by_this_report')
            evidence.write_text('{"ok":false}')
            with self.assertRaises(ValueError):module.report(run)

    def test_incomplete_timing_not_filled_with_zero(self):
        with tempfile.TemporaryDirectory() as temp:
            run=Path(temp)/'run';module.init(run,'VIDEO-26',3)
            report=module.report(run)
            self.assertEqual(report['timing']['status'],'not_measured')

    def test_invalid_video_or_unknown_event_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):module.init(Path(temp)/'bad','VIDEO-26;bad')
            run=Path(temp)/'run';module.init(run,'VIDEO-26')
            with self.assertRaises(ValueError):module.event(run,'approval','not an approval tool')
            with self.assertRaises(ValueError):module.event(run,'candidate_ready','missing evidence')

    def test_unknown_flow_and_no_clobber_report(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):module.init(Path(temp)/'bad','VIDEO-26',4)
            out=Path(temp)/'report.json';module.write_new(out,{'prior':True})
            with self.assertRaises(FileExistsError):module.write_new(out,{'prior':False})
            self.assertEqual(json.loads(out.read_text()),{'prior':True})

    def test_live_version_change_does_not_destroy_historical_report(self):
        with tempfile.TemporaryDirectory() as temp:
            fake=Path(temp)/'framework';(fake/'workflow-profiles').mkdir(parents=True);(fake/'scripts').mkdir()
            for name in ('flujo-2.json','QA_COMUN.md'):
                shutil.copy2(module.ROOT/'workflow-profiles'/name,fake/'workflow-profiles'/name)
            shutil.copy2(module.ROOT/'scripts/medir_fases_edicion.py',fake/'scripts/medir_fases_edicion.py')
            with patch.object(module,'ROOT',fake):
                run=Path(temp)/'run';module.init(run,'VIDEO-26',2)
                (fake/'workflow-profiles/QA_COMUN.md').write_text('new version')
                report=module.report(run)
                self.assertTrue(report['live_rules_changed'])
                with self.assertRaises(ValueError):module.event(run,'full_check','requires new run')

    def test_frozen_rules_tampering_rejects_report(self):
        with tempfile.TemporaryDirectory() as temp:
            run=Path(temp)/'run';module.init(run,'VIDEO-26',2)
            (run/'frozen/QA_COMUN.md').write_text('altered')
            with self.assertRaises(ValueError):module.report(run)

if __name__=='__main__':unittest.main()
