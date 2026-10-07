#!/usr/bin/env python3
"""Experimental, read-only MP4 inspection. Does not replace qa_post_render.py.

Derives scene/caption/image seams from the actual HTML, instead of copying a
previous video's timestamps. CFR, zero-start MP4 only; rejects other profiles.
One decode extracts neighbours and reading states. Visual/audio approval is
always separate from this evidence.
"""
import argparse
import hashlib
import json
import math
import subprocess
import time
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path

from PIL import Image, ImageDraw


class TimelineParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag != 'audio' and 'data-start' in a and 'data-duration' in a:
            self.nodes.append(a)


def collect(project, file=Path('index.html'), offset=0, stack=()):
    path = (project / file).resolve()
    if not path.is_relative_to(project) or path in stack:
        raise ValueError('Non-local or recursive subcomposition')
    parser = TimelineParser()
    parser.feed(path.read_text())
    result = []
    for node in parser.nodes:
        start = offset + float(node['data-start'])
        end = start + float(node['data-duration'])
        if not all(math.isfinite(t) for t in (start, end)) or end <= start:
            raise ValueError('Invalid timeline range')
        result.append({'file': str(path.relative_to(project)),
                       'id': node.get('id', node.get('data-composition-id')),
                       'start': start, 'end': end})
        if 'data-composition-src' in node:
            result += collect(project, Path(node['data-composition-src']),
                              start, (*stack, path))
    # Legacy compositions can drive inner captions purely through GSAP. Their
    # canonical cue file supplies seams that HTML attributes alone cannot find.
    captions = project / 'captions.json'
    if not stack and file == Path('index.html') and captions.exists():
        for n, cue in enumerate(json.loads(captions.read_text())):
            start, end = float(cue['start']), float(cue['end'])
            if not all(math.isfinite(t) for t in (start, end)) or end <= start:
                raise ValueError('Invalid caption range')
            result.append({'file': 'captions.json', 'id': f'cue-{n}',
                           'start': start, 'end': end})
    return result


def selection_expression(indices):
    # FFmpeg's expression parser has a nesting limit. A left-deep sum of many
    # eq() terms can fail; a balanced sum preserves exactly the same indices.
    def balanced(items):
        if len(items) == 1:
            return items[0]
        middle = len(items) // 2
        return f'({balanced(items[:middle])}+{balanced(items[middle:])})'
    return balanced([f'eq(n,{n})' for n in indices])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', required=True, type=Path)
    ap.add_argument('--input', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--ffmpeg', required=True)
    ap.add_argument('--ffprobe', required=True)
    args = ap.parse_args()
    project = args.project.resolve()
    source = args.input.resolve()
    out = args.out.resolve()
    if out.exists():
        raise ValueError('Use a new evidence directory; previous evidence is preserved')
    probe = json.loads(subprocess.check_output([
        args.ffprobe, '-v', 'error', '-show_streams', '-of', 'json', str(source)]))
    v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    rate = Fraction(v['r_frame_rate'])
    if rate != Fraction(v['avg_frame_rate']) or abs(float(v.get('start_time', 0))) > 1e-6:
        raise ValueError('Only zero-start CFR MP4 is verified by this experimental helper')
    fps = float(rate)
    last = int(v['nb_frames']) - 1
    ranges = collect(project)
    bounds = sorted(set(t for r in ranges for t in (r['start'], r['end'])))
    indices = {0, last}
    for t in bounds:
        indices.update(max(0, min(last, round(t * fps) + d)) for d in (-2, -1, 0, 1, 2))
    # Midpoints of every mounted state/caption, plus a one-second overview.
    indices.update(max(0, min(last, round((r['start'] + r['end']) * fps / 2))) for r in ranges)
    indices.update(round(t * fps) for t in range(1, int(last / fps) + 1))
    indices = sorted(indices)
    out.mkdir(parents=True)
    selection = selection_expression(indices)
    hdr = v.get('color_transfer') in ('arib-std-b67', 'smpte2084')
    tone = ('zscale=transfer=linear:npl=100,format=gbrpf32le,'
            'zscale=primaries=bt709,tonemap=tonemap=hable:desat=0,'
            'zscale=transfer=bt709:matrix=bt709:range=limited,format=yuv420p') if hdr else 'format=yuv420p'
    argv = [args.ffmpeg, '-hide_banner', '-y', '-i', str(source), '-vf',
            f"select='{selection}',{tone},scale=360:640", '-fps_mode', 'vfr',
            str(out / 'frame-%03d.png')]
    started = time.monotonic()
    run = subprocess.run(argv, capture_output=True)
    (out / 'extract.log').write_bytes(run.stderr)
    if run.returncode:
        raise RuntimeError(run.stderr.decode(errors='replace')[-1200:])
    files = sorted(out.glob('frame-*.png'))
    if len(files) != len(indices):
        raise ValueError(f'Expected {len(indices)} frames, got {len(files)}')
    for page, start in enumerate(range(0, len(files), 30), 1):
        block = files[start:start + 30]
        sheet = Image.new('RGB', (1296, math.ceil(len(block) / 6) * 408), '#111b23')
        draw = ImageDraw.Draw(sheet)
        for j, file in enumerate(block):
            im = Image.open(file).convert('RGB')
            im.thumbnail((216, 384))
            x, y = (j % 6) * 216, (j // 6) * 408
            sheet.paste(im, (x, y))
            n = indices[start + j]
            draw.text((x + 8, y + 387), f'n={n}, t={n/fps:.3f}s', fill='white')
        sheet.save(out / f'contact-sheet-{page}.jpg', quality=93)
    with source.open('rb') as f:
        sha = hashlib.file_digest(f, 'sha256').hexdigest()
    evidence = {'helper_version': '0.1-experimental', 'source': str(source),
                'source_sha256': sha, 'fps': fps, 'indices': indices,
                'ranges': ranges, 'frame_count': len(files), 'decode_runs': 1,
                'wall_seconds': round(time.monotonic() - started, 3),
                'sampling': 'visual seams -2,-1,0,+1,+2; every state/caption midpoint; 1s overview',
                'color_filter': tone, 'diagnostic_only': True,
                'argv': argv, 'human_listened': False, 'visual_review_completed': False}
    (out / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: evidence[k] for k in ('frame_count', 'decode_runs', 'wall_seconds', 'source_sha256')}))


if __name__ == '__main__':
    main()
