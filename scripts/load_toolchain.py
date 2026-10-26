#!/usr/bin/env python3
"""Load the exact pinned tool image, including recovery of a removed manifest.

The preserved original OCI manifest authenticates every compressed blob; its
config authenticates the uncompressed layer hashes. Docker's load archive uses
those identical config/layer bytes, not a rebuilt or replacement image.
"""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = 'https://ghcr.io/v2/btbn/ffmpeg-builds/win64-lgpl'

def digest(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()

def metadata():
    lock = json.loads((ROOT / 'sources.lock.json').read_text())
    raw_manifest = (ROOT / 'toolchain-oci/manifest.json').read_bytes()
    raw_config = (ROOT / 'toolchain-oci/config.json').read_bytes()
    manifest = json.loads(raw_manifest)
    config = json.loads(raw_config)
    expected = lock['toolchain_image'].split('@', 1)[1]
    assert digest(raw_manifest) == expected, 'Original OCI manifest hash mismatch'
    assert digest(raw_config) == manifest['config']['digest'], 'OCI config hash mismatch'
    assert config['os'] == 'linux' and config['architecture'] == 'amd64'
    assert len(config['rootfs']['diff_ids']) == len(manifest['layers'])
    return lock['toolchain_image'], raw_config, manifest, config

def add_bytes(archive, name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = 0o644
    archive.addfile(info, io.BytesIO(data))

def stream_hash(stream):
    result = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        result.update(chunk)
    return 'sha256:' + result.hexdigest()

def load():
    image, raw_config, manifest, config = metadata()
    evidence = ROOT / 'dist/evidence'
    evidence.mkdir(parents=True, exist_ok=True)
    with (evidence / 'toolchain-pull.log').open('wb') as log:
        pull = subprocess.run(['docker', 'pull', image], stdout=log, stderr=subprocess.STDOUT)
    image_id = manifest['config']['digest']
    proof = {'original_image': image, 'expected_image_id': image_id, 'pull_returncode': pull.returncode,
             'recovered_from_preserved_oci': pull.returncode != 0, 'layers': []}
    try:
        if pull.returncode:
            request = urllib.request.Request(
                'https://ghcr.io/token?scope=repository:btbn/ffmpeg-builds/win64-lgpl:pull',
                headers={'User-Agent': 'libmpv-lgpl-build'})
            with urllib.request.urlopen(request, timeout=60) as response:
                token = json.load(response)['token']
            paths = [f'layers/{item["digest"].split(":")[1]}.tar.gz' for item in manifest['layers']]
            docker_manifest = [{'Config': 'config.json', 'RepoTags': ['libmpv-toolchain:locked'], 'Layers': paths}]
            with tempfile.TemporaryDirectory(prefix='toolchain-cache-', dir=ROOT) as directory:
                with (evidence / 'toolchain-load.log').open('wb') as log:
                    process = subprocess.Popen(['docker', 'load'], stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT)
                    try:
                        with tarfile.open(fileobj=process.stdin, mode='w|') as archive:
                            add_bytes(archive, 'manifest.json', json.dumps(docker_manifest).encode())
                            add_bytes(archive, 'config.json', raw_config)
                            for number, (layer, diff_id, path) in enumerate(zip(manifest['layers'], config['rootfs']['diff_ids'], paths), 1):
                                print(f'Recovering original layer {number}/{len(paths)}: {layer["digest"]}', flush=True)
                                target = Path(directory) / 'layer.gz'
                                request = urllib.request.Request(REGISTRY + '/blobs/' + layer['digest'],
                                    headers={'Authorization': 'Bearer ' + token, 'User-Agent': 'libmpv-lgpl-build'})
                                compressed_hash = hashlib.sha256()
                                with urllib.request.urlopen(request, timeout=180) as response, target.open('wb') as out:
                                    while chunk := response.read(1024 * 1024):
                                        compressed_hash.update(chunk)
                                        out.write(chunk)
                                assert target.stat().st_size == layer['size'], 'Layer size mismatch'
                                assert 'sha256:' + compressed_hash.hexdigest() == layer['digest'], 'Compressed layer hash mismatch'
                                with gzip.open(target, 'rb') as stream:
                                    actual_diff_id = stream_hash(stream)
                                assert actual_diff_id == diff_id, 'Uncompressed layer hash mismatch'
                                info = tarfile.TarInfo(path)
                                info.size = layer['size']
                                info.mode = 0o644
                                with target.open('rb') as stream:
                                    archive.addfile(info, stream)
                                target.unlink()
                                proof['layers'].append({'compressed_digest': layer['digest'], 'diff_id': actual_diff_id, 'bytes': layer['size']})
                        process.stdin.close()
                        assert process.wait() == 0, 'Docker load failed; see toolchain-load.log'
                    finally:
                        if process.poll() is None:
                            process.kill()
                            process.wait()
        inspection = json.loads(subprocess.check_output(['docker', 'image', 'inspect', image_id]))
        assert inspection[0]['Id'] == image_id, 'Recovered image identity mismatch'
        assert inspection[0]['RootFS']['Layers'] == config['rootfs']['diff_ids'], 'Recovered root filesystem mismatch'
        (evidence / 'toolchain-image.json').write_text(json.dumps(inspection, indent=2) + '\n')
        (evidence / 'toolchain-reference.txt').write_text(image_id + '\n')
        proof['verified'] = True
    except Exception as error:
        proof['verified'] = False
        proof['error'] = repr(error)
        raise
    finally:
        (evidence / 'toolchain-recovery.json').write_text(json.dumps(proof, indent=2) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-metadata', action='store_true')
    args = parser.parse_args()
    if args.check_metadata:
        image, _, manifest, _ = metadata()
        print(image, manifest['config']['digest'], len(manifest['layers']), 'layers; metadata verified')
    else:
        load()
