#!/usr/bin/env python3
"""Standalone synthetic-media C API checks; imports no application code."""
import argparse
import ctypes as C
from ctypes import wintypes as W
import hashlib
import json
import os
from pathlib import Path
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument('--dll', type=Path, required=True)
parser.add_argument('--media', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--warp', action='store_true')
parser.add_argument('--wasapi', action='store_true')
parser.add_argument('--pyav', choices=['first', 'last'])
parser.add_argument('--graphics-api', choices=['d3d11', 'opengl', 'vulkan'])
parser.add_argument('--graphics-context')
parser.add_argument('--graphics-only', action='store_true')
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
report = {'checks': {}, 'dll_sha256': hashlib.sha256(args.dll.read_bytes()).hexdigest(), 'python': sys.version}
logs = []
av = None
if args.pyav == 'first':
    import av

dll_search = os.add_dll_directory(str(args.dll.resolve().parent))
lib = C.CDLL(str(args.dll.resolve()))
lib.mpv_create.restype = C.c_void_p
lib.mpv_initialize.argtypes = [C.c_void_p]
lib.mpv_initialize.restype = C.c_int
lib.mpv_set_option_string.argtypes = [C.c_void_p, C.c_char_p, C.c_char_p]
lib.mpv_set_option_string.restype = C.c_int
lib.mpv_set_property_string.argtypes = [C.c_void_p, C.c_char_p, C.c_char_p]
lib.mpv_set_property_string.restype = C.c_int
lib.mpv_get_property_string.argtypes = [C.c_void_p, C.c_char_p]
lib.mpv_get_property_string.restype = C.c_void_p
lib.mpv_free.argtypes = [C.c_void_p]
lib.mpv_command.argtypes = [C.c_void_p, C.POINTER(C.c_char_p)]
lib.mpv_command.restype = C.c_int
lib.mpv_terminate_destroy.argtypes = [C.c_void_p]
lib.mpv_request_log_messages.argtypes = [C.c_void_p, C.c_char_p]
class Event(C.Structure):
    _fields_ = [('event_id', C.c_int), ('error', C.c_int), ('reply_userdata', C.c_uint64), ('data', C.c_void_p)]
class Log(C.Structure):
    _fields_ = [('prefix', C.c_char_p), ('level', C.c_char_p), ('text', C.c_char_p), ('log_level', C.c_int)]
lib.mpv_wait_event.argtypes = [C.c_void_p, C.c_double]
lib.mpv_wait_event.restype = C.POINTER(Event)

user = C.WinDLL('user32', use_last_error=True)
kernel = C.WinDLL('kernel32', use_last_error=True)
user.CreateWindowExW.argtypes = [W.DWORD, W.LPCWSTR, W.LPCWSTR, W.DWORD, C.c_int, C.c_int, C.c_int, C.c_int, W.HWND, W.HMENU, W.HINSTANCE, C.c_void_p]
user.CreateWindowExW.restype = W.HWND
user.DestroyWindow.argtypes = [W.HWND]
kernel.GetModuleHandleW.argtypes = [W.LPCWSTR]
kernel.GetModuleHandleW.restype = W.HMODULE
window = user.CreateWindowExW(0x08000080, 'STATIC', 'Isolated libmpv probe', 0x80000000,
                              -32000, -32000, 640, 360, None, None, kernel.GetModuleHandleW(None), None)
if not window:
    raise C.WinError(C.get_last_error())
handle = lib.mpv_create()

def check(name, condition, detail=None):
    report['checks'][name] = {'passed': bool(condition), 'detail': detail}
    if not condition:
        raise AssertionError(f'{name}: {detail}')

def drain():
    for _ in range(100):
        event = lib.mpv_wait_event(handle, 0).contents
        if event.event_id == 0:
            break
        if event.event_id == 2 and event.data:
            entry = C.cast(event.data, C.POINTER(Log)).contents
            logs.append((entry.prefix or b'').decode(errors='replace') + ': ' + (entry.text or b'').decode(errors='replace'))

def prop(name):
    value = lib.mpv_get_property_string(handle, name.encode())
    if not value:
        return None
    try:
        return C.string_at(value).decode(errors='replace')
    finally:
        lib.mpv_free(value)

def setprop(name, value):
    rc = lib.mpv_set_property_string(handle, name.encode(), str(value).encode())
    if rc < 0:
        raise RuntimeError(f'property {name}: {rc}')

def command(*values):
    array = (C.c_char_p * (len(values) + 1))(*(str(v).encode() for v in values), None)
    rc = lib.mpv_command(handle, array)
    if rc < 0:
        raise RuntimeError(f'command {values[0]}: {rc}')

def wait(predicate, timeout=10):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        drain()
        if predicate():
            return True
        time.sleep(.025)
    drain()
    return False

def position():
    return float(prop('time-pos') or -1)

def seek(seconds, mode='absolute+exact'):
    command('seek', seconds, mode)
    return wait(lambda: prop('seeking') == 'no' and abs(position() - seconds) < .12)

def modules():
    psapi = C.WinDLL('psapi', use_last_error=True)
    kernel.GetCurrentProcess.restype = W.HANDLE
    process = kernel.GetCurrentProcess()
    psapi.EnumProcessModules.argtypes = [W.HANDLE, C.POINTER(W.HMODULE), W.DWORD, C.POINTER(W.DWORD)]
    psapi.GetModuleFileNameExW.argtypes = [W.HANDLE, W.HMODULE, W.LPWSTR, W.DWORD]
    handles = (W.HMODULE * 2048)()
    needed = W.DWORD()
    if not psapi.EnumProcessModules(process, handles, C.sizeof(handles), C.byref(needed)):
        raise C.WinError(C.get_last_error())
    found = []
    for module in handles[:needed.value // C.sizeof(W.HMODULE)]:
        path = C.create_unicode_buffer(32768)
        if psapi.GetModuleFileNameExW(process, module, path, len(path)):
            file = Path(path.value)
            name = file.name.lower()
            if any(part in name for part in ('libmpv', 'avcodec', 'avformat', 'avutil', 'avfilter', 'avdevice', 'swresample', 'swscale', 'x264', 'x265')):
                found.append({'name': file.name, 'path': str(file).replace(sys.prefix, '%PYTHON_PREFIX%'), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
    return found

try:
    lib.mpv_request_log_messages(handle, b'v')
    options = {'wid': str(window), 'vo': 'gpu', 'hwdec': 'auto-safe', 'keep-open': 'always',
               'pause': 'yes', 'keepaspect': 'yes', 'input-default-bindings': 'no', 'input-vo-keyboard': 'no',
               'osc': 'no', 'cache': 'yes', 'demuxer-max-bytes': str(200*1024*1024),
               'demuxer-max-back-bytes': str(200*1024*1024), 'hr-seek': 'yes',
               'ao': 'wasapi' if args.wasapi else 'null', 'volume': '0', 'config': 'no'}
    if args.warp:
        options.update({'gpu-api': 'd3d11', 'gpu-context': 'd3d11', 'd3d11-warp': 'yes'})
    if args.graphics_api:
        options['gpu-api'] = args.graphics_api
    if args.graphics_context:
        options['gpu-context'] = args.graphics_context
    report['requested_graphics'] = {'api': options.get('gpu-api', 'auto'), 'context': options.get('gpu-context', 'auto'), 'warp': args.warp}
    for name, value in options.items():
        check('option:' + name, lib.mpv_set_option_string(handle, name.encode(), value.encode()) >= 0)
    check('initialize', lib.mpv_initialize(handle) >= 0)
    if args.pyav == 'last':
        import av
    report['versions'] = {name: prop(name) for name in ('mpv-version', 'ffmpeg-version', 'mpv-configuration')}
    command('loadfile', str(args.media.resolve()))
    check('load', wait(lambda: prop('vo-configured') == 'yes' and prop('audio-params/samplerate') is not None), prop('current-vo'))
    report['output'] = {name: prop(name) for name in ('current-vo', 'current-gpu-context', 'current-ao', 'hwdec-current', 'audio-params', 'video-params')}
    check('audio_output', prop('current-ao') == ('wasapi' if args.wasapi else 'null'), report['output'])
    check('metadata', float(prop('duration') or 0) >= 4 and int(prop('video-params/w') or 0) == 320)
    setprop('pause', 'no')
    check('playback', wait(lambda: position() > .3))
    setprop('pause', 'yes')
    paused = position()
    time.sleep(.25)
    check('pause', abs(position() - paused) < .08, [paused, position()])
    if args.graphics_only:
        image = args.output / 'graphics.png'
        command('screenshot-to-file', str(image.resolve()), 'video')
        check('graphics_capture', wait(lambda: image.exists() and image.stat().st_size > 100))
        check('graphics_png', image.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))
        report['graphics_png_sha256'] = hashlib.sha256(image.read_bytes()).hexdigest()
        report['loaded_modules'] = modules()
        report['success'] = True
        raise SystemExit(0)
    check('seek_exact', seek(2), position())
    command('seek', 1.5, 'absolute+keyframes')
    check('scrub_preview', wait(lambda: prop('seeking') == 'no' and 0 <= position() < 1.8), position())
    check('scrub_release', seek(2.5), position())
    before = position()
    command('frame-step')
    check('frame_step', wait(lambda: position() > before + .015), [before, position()])
    before = position()
    command('frame-back-step')
    check('frame_back_step', wait(lambda: position() < before - .015), [before, position()])
    check('reverse_start', seek(3))
    setprop('play-dir', 'backward')
    setprop('pause', 'no')
    check('reverse', wait(lambda: 0 <= position() < 2.8), position())
    setprop('pause', 'yes')
    setprop('play-dir', 'forward')
    length = float(prop('duration'))
    check('seek_near_eof', seek(length - .3), position())
    setprop('pause', 'no')
    check('eof', wait(lambda: prop('eof-reached') == 'yes'), position())
    end = position()
    command('frame-back-step')
    check('recover_frame_from_eof', wait(lambda: position() < end - .015), [end, position()])
    check('navigation_after_eof', seek(1), position())
    image = args.output / 'preview.png'
    command('screenshot-to-file', str(image.resolve()), 'video')
    check('preview_capture', wait(lambda: image.exists() and image.stat().st_size > 100), str(image.name))
    check('preview_png', image.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))
    command('loadfile', str(image.resolve()))
    check('preview_load', wait(lambda: prop('video-format') == 'png' and prop('vo-configured') == 'yes'), prop('video-format'))

    if av is not None:
        report['pyav'] = {'version': av.__version__, 'libraries': av.library_versions}
        check('pyav_version', av.__version__ == '18.1.0')
        with av.open(str(args.media)) as container:
            video = container.streams.video[0]
            check('pyav_metadata', video.width == 320 and container.duration > 0)
        with av.open(str(args.media)) as container:
            frames = list(container.decode(audio=0))
            samples = sum(f.samples for f in frames)
            amplitude = float(max(abs(f.to_ndarray()).max() for f in frames))
            check('pyav_audio_decode', samples > 100000 and amplitude > 0, {'samples': samples, 'amplitude': amplitude})
        with av.open(str(args.media)) as container:
            video = container.streams.video[0]
            duration = container.duration / av.time_base
            container.seek(int((duration - 1) / video.time_base), stream=video, backward=True)
            times = [float(frame.time) for frame in container.decode(video=0) if frame.time is not None]
            check('pyav_eof_frames', bool(times) and duration - .12 < times[-1] < duration + .12, {'last': times[-1] if times else None, 'duration': duration})
    report['loaded_modules'] = modules()
    check('no_gpl_codec_dlls', not any('x264' in item['name'].lower() or 'x265' in item['name'].lower() for item in report['loaded_modules']))
    if av is not None:
        core = [item for item in report['loaded_modules'] if item['name'].lower().startswith(('avcodec-', 'avformat-', 'avutil-'))]
        check('pyav_core_dlls_loaded', len(core) == 3, core)
        for item in core:
            dll = C.CDLL(item['path'].replace('%PYTHON_PREFIX%', sys.prefix))
            name = item['name'].split('-')[0]
            func = getattr(dll, name + '_license')
            func.restype = C.c_char_p
            item['license'] = func().decode()
            check(name + '_lgpl', 'LGPL' in item['license'], item['license'])
    report['success'] = True
except Exception as error:
    report['success'] = False
    report['error'] = repr(error)
    raise
finally:
    drain()
    (args.output / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    (args.output / 'mpv.log').write_text(''.join(logs), encoding='utf-8')
    lib.mpv_terminate_destroy(handle)
    user.DestroyWindow(window)
