"""Servidor localhost con rangos HTTP para comparar MP4 sin perder el seek.

Convive con el banco anterior en8866. Sirve solo el framework ya expuesto allí.
"""
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

FRAMEWORK = Path(__file__).resolve().parents[3]


class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = Path(self.translate_path(self.path)).resolve()
        if not path.is_relative_to(FRAMEWORK):
            self.send_error(404)
            return None
        self.byte_range = None
        header = self.headers.get('Range')
        if not header or not path.is_file():
            return super().send_head()
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', header)
        size = path.stat().st_size
        if not match or not any(match.groups()):
            self.send_error(416)
            return None
        a, b = match.groups()
        start = int(a) if a else max(0, size-int(b))
        end = min(size-1, int(b)) if a and b else size-1
        if start >= size or end < start:
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.end_headers()
            return None
        f = path.open('rb')
        f.seek(start)
        self.byte_range = (start, end)
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(str(path)))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end-start+1))
        self.end_headers()
        return f

    def copyfile(self, source, outputfile):
        if self.byte_range is None:
            return super().copyfile(source, outputfile)
        left = self.byte_range[1]-self.byte_range[0]+1
        while left:
            data = source.read(min(left, 256*1024))
            if not data:
                break
            outputfile.write(data)
            left -= len(data)


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 8868), partial(RangeHandler, directory=str(FRAMEWORK)))
    print('Comparaciones: http://127.0.0.1:8868/research/musica-bajo-voz-2026-09-30/practica.html', flush=True)
    server.serve_forever()
