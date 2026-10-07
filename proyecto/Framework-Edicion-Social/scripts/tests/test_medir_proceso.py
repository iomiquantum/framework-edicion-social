import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from datetime import datetime, timezone, timedelta

spec = importlib.util.spec_from_file_location('medir_proceso', Path(__file__).resolve().parents[1] / 'medir_proceso.py')
timer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(timer)


class ProcessMeasurements(unittest.TestCase):
    def test_failure_logs_and_unique_attempts(self):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, '-c', "import sys; print('salida'); print('fallo', file=sys.stderr); sys.exit(7)"]
            first, event = timer.measure(out=directory, scope='VIDEO-16', phase='check', command=command)
            second, _ = timer.measure(out=directory, scope='VIDEO-16', phase='check', command=command)
            self.assertNotEqual(first, second)
            self.assertEqual(event['exit_code'], 7)
            self.assertGreater(event['wall_s'], 0)
            self.assertIn('fallo', (first / 'stderr.log').read_text())
            self.assertEqual(timer.summarize(directory)['phases']['check']['failed'], 2)

    def test_literal_argument_no_shell_and_scope_filter(self):
        with tempfile.TemporaryDirectory() as directory:
            literal = '$(touch SHOULD_NOT_EXIST); `echo unsafe`'
            path, event = timer.measure(out=directory, scope='LOTE-16-20', phase='ingesta', command=[sys.executable, '-c', 'import sys; print(sys.argv[1])', literal], cwd=directory)
            self.assertEqual((path / 'stdout.log').read_text().strip(), literal)
            self.assertFalse((Path(directory) / 'SHOULD_NOT_EXIST').exists())
            self.assertEqual(event['status'], 'pass')
            self.assertEqual(timer.summarize(directory, 'VIDEO-16')['events'], 0)

    def test_modified_log_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = timer.measure(out=directory, scope='VIDEO-16', phase='check', command=[sys.executable, '-c', 'print(1)'])
            (path / 'stdout.log').write_text('alterado')
            with self.assertRaisesRegex(ValueError, 'Log alterado'):
                timer.summarize(directory)

    def test_overlapping_intervals_do_not_double_count(self):
        start = datetime(2026, 9, 30, tzinfo=timezone.utc)
        pairs = [(start, start + timedelta(seconds=10)), (start + timedelta(seconds=5), start + timedelta(seconds=15))]
        self.assertEqual(timer.interval_union_seconds(pairs), 15)

    def test_launch_failure_is_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            path, event = timer.measure(out=directory, scope='VIDEO-16', phase='check', command=[str(Path(directory) / 'missing-command')])
            self.assertEqual(event['exit_code'], 127)
            self.assertIsNotNone(event['launch_error'])
            self.assertTrue((path / 'event.json').exists())


if __name__ == '__main__':
    unittest.main()
