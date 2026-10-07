import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from uuid import UUID


SCRIPT = Path(__file__).resolve().parents[1] / 'medir_fases_edicion.py'
spec = importlib.util.spec_from_file_location('medir_fases_edicion', SCRIPT)
timer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(timer)


class PhaseMeasurements(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.run = Path(self.temporary.name) / 'pilot'

    def tearDown(self):
        self.temporary.cleanup()

    def interval(self, phase, start, stop, *, kind='work'):
        timer.start_interval(self.run, phase, kind=kind, clock=lambda: start)
        timer.stop_interval(self.run, clock=lambda: stop)

    def test_lifecycle_append_only_and_preserves_run_metadata(self):
        self.run.mkdir()
        metadata = b'{"profile":"flow2","approved":false}\n'
        (self.run / 'run.json').write_bytes(metadata)
        start = timer.start_interval(self.run, 'assembly', note='primer montaje', clock=lambda: 100)
        original = (self.run / 'timing/events' / (start['event_id'] + '.json')).read_bytes()
        with self.assertRaisesRegex(ValueError, 'Ya existe'):
            timer.start_interval(self.run, 'render', clock=lambda: 101)
        stop = timer.stop_interval(self.run, note='terminado', clock=lambda: 104.5)
        with self.assertRaisesRegex(ValueError, 'No existe'):
            timer.stop_interval(self.run, clock=lambda: 105)
        self.assertEqual((self.run / 'run.json').read_bytes(), metadata)
        self.assertEqual((self.run / 'timing/events' / (start['event_id'] + '.json')).read_bytes(), original)
        self.assertNotEqual(start['event_id'], stop['event_id'])
        self.assertEqual(str(UUID(start['event_id'])), start['event_id'])
        self.assertEqual(stop['interval_id'], start['event_id'])
        state = json.loads((self.run / 'timing/state.json').read_text())
        self.assertIsNone(state['open_interval'])
        report = timer.summarize(self.run)
        self.assertEqual(report['observed_union_seconds'], 4.5)
        self.assertEqual(report['intervals'][0]['start_note'], 'primer montaje')
        self.assertEqual(report['intervals'][0]['stop_note'], 'terminado')
        self.assertFalse(list((self.run / 'timing').rglob('.pending-*')))

    def test_holes_waits_audit_and_unmeasured_phases_are_distinct(self):
        self.interval('assembly', 100, 110)
        self.interval('coordination', 120, 125, kind='user_wait')
        self.interval('qa_post_render', 125, 128, kind='experiment_audit')
        self.interval('render', 128, 130, kind='command')
        self.interval('documentation', 130, 130)
        report = timer.summarize(self.run)
        self.assertEqual(report['elapsed_span_seconds'], 30)
        self.assertEqual(report['observed_union_seconds'], 20)
        self.assertEqual(report['unmeasured_gaps_seconds'], 10)
        self.assertEqual(report['kinds']['work']['total_seconds'], 10)
        self.assertEqual(report['kinds']['command']['total_seconds'], 2)
        self.assertEqual(report['kinds']['user_wait']['total_seconds'], 5)
        self.assertEqual(report['kinds']['experiment_audit']['total_seconds'], 3)
        self.assertEqual(report['observed_operational_union_seconds'], 12)
        self.assertEqual(report['observed_user_wait_seconds'], 5)
        self.assertEqual(report['observed_experiment_audit_seconds'], 3)
        self.assertEqual(report['phases']['documentation']['status'], 'measured')
        self.assertEqual(report['phases']['documentation']['total_seconds'], 0)
        self.assertEqual(report['phases']['intake']['status'], 'not_measured')
        self.assertIsNone(report['phases']['intake']['total_seconds'])

    def test_union_does_not_double_count_and_rejects_invalid_intervals(self):
        self.assertEqual(timer.interval_union_seconds([(5, 15), (0, 10), (18, 20), (20, 20)]), 17)
        self.assertEqual(timer.interval_union_seconds([]), 0)
        for pairs in ([(3, 2)], [(0, float('inf'))], [(float('nan'), 1)]):
            with self.assertRaises(ValueError):
                timer.interval_union_seconds(pairs)

    def test_invalid_phase_kind_or_clock_cannot_commit_an_event(self):
        for phase, kind in (('invented', 'work'), ('assembly', 'unknown')):
            with self.assertRaisesRegex(ValueError, 'desconocido'):
                timer.start_interval(self.run, phase, kind=kind, clock=lambda: 100)
        self.assertFalse(self.run.exists())
        with self.assertRaisesRegex(ValueError, 'finitos'):
            timer.start_interval(self.run, 'assembly', clock=lambda: float('nan'))
        self.assertEqual(timer.summarize(self.run)['events'], 0)

    def test_backwards_clock_rejected_without_losing_open_interval(self):
        self.interval('intake', 90, 100)
        with self.assertRaisesRegex(ValueError, 'retrocedió'):
            timer.start_interval(self.run, 'assembly', clock=lambda: 99)
        timer.start_interval(self.run, 'assembly', clock=lambda: 110)
        with self.assertRaisesRegex(ValueError, 'retrocedió'):
            timer.stop_interval(self.run, clock=lambda: 109)
        report = timer.summarize(self.run)
        self.assertEqual(report['events'], 3)
        self.assertEqual(report['open_interval']['phase'], 'assembly')
        self.assertEqual(report['observed_union_seconds'], 10)
        timer.stop_interval(self.run, clock=lambda: 120)

    def test_journal_recovers_stale_state_and_open_time_is_not_counted(self):
        timer.start_interval(self.run, 'qa_pre_render', clock=lambda: 100)
        (self.run / 'timing/state.json').write_text('{"open_interval":null}')
        report = timer.summarize(self.run)
        self.assertEqual(report['status'], 'in_progress')
        self.assertIsNone(report['observed_union_seconds'])
        self.assertIsNone(report['elapsed_span_seconds'])
        self.assertEqual(report['phases']['qa_pre_render']['status'], 'not_measured')
        with self.assertRaisesRegex(ValueError, 'Ya existe'):
            timer.start_interval(self.run, 'render', clock=lambda: 105)
        timer.stop_interval(self.run, clock=lambda: 106)
        report = timer.summarize(self.run)
        self.assertEqual(report['observed_union_seconds'], 6)
        self.assertEqual(report['closed_intervals'], 1)

    def test_concurrent_cli_starts_allow_only_one_open_interval(self):
        command = [sys.executable, str(SCRIPT), 'start', '--run', str(self.run), '--phase', 'assembly']
        processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        outputs = [process.communicate(timeout=10) for process in processes]
        self.assertEqual(sorted(process.returncode for process in processes), [0, 2])
        report = timer.summarize(self.run)
        self.assertEqual(report['events'], 1)
        self.assertIsNotNone(report['open_interval'])
        self.assertTrue(any('Ya existe' in error for _, error in outputs))
        stopped = subprocess.run([sys.executable, str(SCRIPT), 'stop', '--run', str(self.run)], capture_output=True, text=True, timeout=10)
        self.assertEqual(stopped.returncode, 0, stopped.stderr)
        summarized = subprocess.run([sys.executable, str(SCRIPT), 'summary', '--run', str(self.run)], capture_output=True, text=True, timeout=10)
        self.assertEqual(summarized.returncode, 0, summarized.stderr)
        self.assertEqual(json.loads(summarized.stdout)['closed_intervals'], 1)

    def test_empty_summary_and_invalid_journal_fail_explicitly(self):
        report = timer.summarize(self.run)
        self.assertEqual(report['status'], 'not_measured')
        for key in ('elapsed_span_seconds', 'observed_union_seconds', 'unmeasured_gaps_seconds',
                    'observed_operational_union_seconds', 'observed_user_wait_seconds',
                    'observed_experiment_audit_seconds'):
            self.assertIsNone(report[key])
        start = timer.start_interval(self.run, 'assembly', clock=lambda: 100)
        path = self.run / 'timing/events' / (start['event_id'] + '.json')
        modified = json.loads(path.read_text())
        modified['sequence'] = 2
        path.write_text(json.dumps(modified))
        with self.assertRaisesRegex(ValueError, 'secuencias'):
            timer.summarize(self.run)
        with self.assertRaisesRegex(ValueError, 'secuencias'):
            timer.stop_interval(self.run, clock=lambda: 105)
        self.assertEqual(len(list((self.run / 'timing/events').glob('*.json'))), 1)


if __name__ == '__main__':
    unittest.main()
