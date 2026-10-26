#!/usr/bin/env python3
"""Record only public package identities and actually loaded FFmpeg DLLs."""
import ctypes as C
from ctypes import wintypes as W
import hashlib
import json
from pathlib import Path
import sys
import av

prefix = Path(sys.prefix)
packages = [json.loads(p.read_text()) for p in (prefix / 'conda-meta').glob('*.json')]
forbidden = [p['name'] for p in packages if p['name'] in ('x264', 'x265', 'fftw')]
forbidden_files = [p.name for p in (prefix / 'Library' / 'bin').glob('*.dll') if any(x in p.name.lower() for x in ('x264', 'x265', 'fftw'))]
assert not forbidden and not forbidden_files, (forbidden, forbidden_files)
kernel = C.WinDLL('kernel32', use_last_error=True)
kernel.GetModuleHandleW.argtypes = [W.LPCWSTR]
kernel.GetModuleHandleW.restype = W.HMODULE
kernel.GetModuleFileNameW.argtypes = [W.HMODULE, W.LPWSTR, W.DWORD]
loaded = []
for name, version in av.library_versions.items():
    component = name.removeprefix('lib')
    filename = f'{component}-{version[0]}.dll'
    handle = kernel.GetModuleHandleW(filename)
    assert handle, filename
    path = C.create_unicode_buffer(32768)
    assert kernel.GetModuleFileNameW(handle, path, len(path)), filename
    actual = Path(path.value)
    assert actual.resolve().is_relative_to(prefix.resolve()), actual.name
    dll = C.CDLL(str(actual))
    license_func = getattr(dll, component + '_license')
    license_func.restype = C.c_char_p
    config_func = getattr(dll, component + '_configuration')
    config_func.restype = C.c_char_p
    license_text = license_func().decode()
    configuration = config_func().decode()
    assert 'LGPL' in license_text and '--disable-gpl' in configuration
    assert '--enable-gpl' not in configuration
    loaded.append({'file': filename, 'relative_path': actual.relative_to(prefix).as_posix(),
                   'version': version, 'license': license_text, 'configuration': configuration,
                   'sha256': hashlib.sha256(actual.read_bytes()).hexdigest()})
result = {'python': sys.version, 'pyav': av.__version__, 'loaded_ffmpeg_dlls': loaded,
          'forbidden_packages': forbidden, 'forbidden_dlls': forbidden_files,
          'packages': [{key: p.get(key) for key in ('name','version','build','url','sha256','license')} for p in packages]}
Path(sys.argv[1]).write_text(json.dumps(result, indent=2), encoding='utf-8')
print('Verified:', av.__version__, len(loaded), 'loaded LGPL FFmpeg DLLs; no x264/x265/FFTW')
