#!/usr/bin/env python3
"""Block known production labels in active HTML; emit text inventory for editorial QA.

This narrow gate detects known labels, not every possible editorial mistake.
Internal filenames/IDs and recorded captions are not audience navigation labels.
"""
import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

FORBIDDEN = {'la pregunta', 'el contraste', 'el ejemplo', 'un ejemplo',
             'la idea', 'tu experiencia', 'la promesa', 'el mito', 'el límite',
             'hook', 'pattern break', 'caption', 'cierre', 'intro', 'desarrollo'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr'}

def normalized(text):
    text = re.sub(r'\s+', ' ', text).strip().casefold()
    text = re.sub(r'^\d+\s*[·:/|.−—-]\s*', '', text)
    return re.sub(r'^(sigue|después|siguiente|etapa|fase|paso)\s*:\s*', '', text)

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.texts, self.references = [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('data-composition-src'):
            self.references.append(attrs['data-composition-src'])
        inherited = self.stack[-1]['skip'] if self.stack else False
        classes = attrs.get('class', '').split()
        skip = inherited or tag in {'head', 'script', 'style', 'audio', 'video'}
        skip = skip or any(c in {'caption', 'captions'} for c in classes)
        skip = skip or attrs.get('data-track-kind') == 'captions'
        skip = skip or bool(re.search(r'display\s*:\s*none', attrs.get('style', '')))
        if tag not in VOID:
            self.stack.append({'tag': tag, 'skip': skip, 'chunks': [],
                               'line': self.getpos()[0]})

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if self.stack and self.stack[-1]['skip']:
            return
        for node in self.stack:
            if not node['skip']:
                node['chunks'].append(data)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i]['tag'] == tag:
                nodes, self.stack = self.stack[i:], self.stack[:i]
                for node in nodes:
                    text = re.sub(r'\s+', ' ', ''.join(node['chunks'])).strip()
                    if not node['skip'] and text:
                        self.texts.append({'text': text, 'line': node['line']})
                break

def audit(project):
    project = Path(project).resolve()
    pending, visited, inventory, errors, hashes = [project/'index.html'], set(), [], [], {}
    while pending:
        path = pending.pop()
        if path in visited:
            continue
        visited.add(path)
        if not path.is_relative_to(project) or not path.is_file():
            errors.append({'file': str(path), 'error': 'missing_or_external_active_html'})
            continue
        raw = path.read_bytes()
        hashes[str(path.relative_to(project))] = hashlib.sha256(raw).hexdigest()
        parser = VisibleText()
        parser.feed(raw.decode('utf-8'))
        for row in parser.texts:
            row = {**row, 'file': str(path.relative_to(project))}
            inventory.append(row)
            if normalized(row['text']) in FORBIDDEN:
                errors.append({**row, 'error': 'visible_production_label'})
        pending.extend((project/ref).resolve() for ref in parser.references)
    return {'status': 'fail' if errors else 'pass', 'errors': errors,
            'active_html_sha256': hashes, 'text_inventory': inventory,
            'limits': 'Known labels only; semantic and visual review of all audience text remains mandatory. Captions/technical IDs are excluded.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.project)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(f"Visible text: {result['status']}; {len(result['errors'])} production labels/errors; report {args.report}")
    return 1 if result['errors'] else 0

if __name__ == '__main__':
    raise SystemExit(main())
