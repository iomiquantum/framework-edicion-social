import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('visible', Path(__file__).parents[1]/'validar_texto_visible.py')
visible = importlib.util.module_from_spec(spec)
spec.loader.exec_module(visible)

class VisibleTextTests(unittest.TestCase):
    def audit(self, html, scene=None):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p/'index.html').write_text(html)
            if scene is not None:
                (p/'scene.html').write_text(scene)
            return visible.audit(p)

    def test_numbered_and_anticipation_labels_block(self):
        r = self.audit('<div>01 · LA PREGUNTA</div><div>SIGUE: UN EJEMPLO</div>')
        self.assertEqual(len(r['errors']), 2)

    def test_active_nested_label_blocks(self):
        r = self.audit('<div data-composition-src="scene.html"></div>', '<template><div><span>EL </span><span>CONTRASTE</span></div></template>')
        self.assertEqual(r['status'], 'fail')

    def test_internal_ids_scripts_captions_and_hidden_notes_do_not_block(self):
        r = self.audit('<head><title>LA IDEA</title></head><div id="hook">LO QUE HACES</div><script>"EL EJEMPLO"</script><p class="caption">la pregunta</p><div style="display:none">CIERRE</div>')
        self.assertEqual(r['status'], 'pass')

    def test_contextual_language_passes(self):
        r = self.audit('<div>03 · LO QUE COMPRAS</div><h1>La pregunta que hace el cliente</h1><div>LAS ACCIONES TAMBIÉN HABLAN</div>')
        self.assertEqual(r['status'], 'pass')

    def test_missing_active_subcomposition_fails_closed(self):
        self.assertEqual(self.audit('<div data-composition-src="absent.html"></div>')['status'], 'fail')

if __name__ == '__main__':
    unittest.main()
