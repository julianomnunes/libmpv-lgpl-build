#!/usr/bin/env python3
"""Apply only the reviewed build-time iconv discovery change to pinned MPV."""
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_SHA256 = '26ac765a1f6c685ec8678ccdd313187ad5c1871e74924dad11d6c412dfd88074'
path = ROOT / 'sources/mpv/meson.build'
raw = path.read_bytes()
assert hashlib.sha256(raw).hexdigest() == ORIGINAL_SHA256, 'Pinned MPV Meson source differs'
original = raw.decode()
needle = "iconv = dependency('iconv', required: get_option('iconv'))"
assert original.count(needle) == 1, 'Expected exactly one iconv discovery statement'
snippet = (ROOT / 'scripts/iconv-preflight/resolve-iconv/meson.build').read_text().strip()
assert 'static: true' in snippet and "required: get_option('iconv')" in snippet
updated = original.replace(needle, snippet)
path.write_text(updated, encoding='utf-8', newline='\n')
evidence = ROOT / 'dist/evidence'
evidence.mkdir(parents=True, exist_ok=True)
(evidence / 'mpv-iconv-discovery.patch').write_text(''.join(difflib.unified_diff(
    original.splitlines(keepends=True), updated.splitlines(keepends=True),
    fromfile='a/meson.build', tofile='b/meson.build')), newline='\n')
(evidence / 'mpv-iconv-discovery.json').write_text(json.dumps({
    'original_meson_sha256': ORIGINAL_SHA256,
    'patched_meson_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    'shared_resolution_snippet_sha256': hashlib.sha256(snippet.encode()).hexdigest(),
    'change': 'Required static iconv lookup with explicit controlled prefix directory',
}, indent=2) + '\n', newline='\n')
print('Pinned MPV iconv lookup patched; exact shared Meson snippet and diff recorded')
