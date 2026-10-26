#!/usr/bin/env python3
"""Fetch only hash-locked public source archives; collect sources and notices."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def fetch(item, refresh):
    archive = ROOT / 'archives' / (item['name'] + '.tar.gz')
    archive.parent.mkdir(exist_ok=True)
    if not archive.exists():
        request = urllib.request.Request(item['url'], headers={'User-Agent': 'libmpv-lgpl-build-source-lock'})
        with urllib.request.urlopen(request, timeout=120) as response, archive.open('wb') as out:
            shutil.copyfileobj(response, out)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if not refresh and digest != item['sha256']:
        raise RuntimeError(f"Source hash mismatch: {item['name']}")
    item['sha256'] = digest
    target = ROOT / 'sources' / item.get('path', item['name'])
    ready = ROOT / 'source-state' / item['name']
    if not ready.exists():
        target.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive) as tar:
            members = tar.getmembers()
            prefix = members[0].name.split('/')[0] + '/'
            for member in members:
                if not member.name.startswith(prefix):
                    continue
                member.name = member.name[len(prefix):]
                if member.name:
                    tar.extract(member, target, filter='data')
        ready.parent.mkdir(exist_ok=True)
        ready.write_text(digest + '\n')
    print(item['name'], digest, flush=True)
    return item

def collect(lock):
    destination = ROOT / 'dist' / 'notices'
    destination.mkdir(parents=True, exist_ok=True)
    summary = []
    for item in lock['sources']:
        source = ROOT / 'sources' / item.get('path', item['name'])
        copied = []
        for path in source.rglob('*'):
            relative = path.relative_to(source)
            if not path.is_file() or path.is_symlink() or any(p.startswith('.') for p in relative.parts):
                continue
            name = path.name.upper()
            if name.startswith(('COPYING', 'COPYRIGHT', 'LICENSE', 'LICENCE', 'NOTICE')) or name in ('FTL.TXT', 'AUTHORS'):
                target = destination / item['name'] / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
                copied.append(relative.as_posix())
        summary.append({**item, 'notice_files': copied})
    (ROOT / 'dist' / 'source-and-license-manifest.json').write_text(json.dumps(summary, indent=2) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lock', action='store_true', help='Maintainer-only initial source hash enrollment')
    parser.add_argument('--collect', action='store_true')
    args = parser.parse_args()
    lock_path = ROOT / 'sources.lock.json'
    lock = json.loads(lock_path.read_text())
    if args.collect:
        collect(lock)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            items = list(executor.map(lambda item: fetch(item, args.lock), lock['sources']))
        if args.lock:
            lock['sources'] = items
            lock_path.write_text(json.dumps(lock, indent=2) + '\n', newline='\n')
