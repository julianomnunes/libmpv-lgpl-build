# Isolated Windows x64 libmpv build

**Current result: clean builds 6 and 7 produced an identical DLL; run 7 passed all 50 Windows smoke checks.**
The EOF harness correction was validated against the preserved DLL and R5.
Native WASAPI/D3D11VA and both PyAV load orders passed with the exact same DLL
bytes. All seven executions are first attempts; the authorized budget is spent.
**Vulkan/R5 equivalence remains blocked and redistribution is not approved.**
The earlier failures, original DLLs and source/license evidence are preserved.
See [BUILD_STATUS.md](BUILD_STATUS.md) for the exact failures, artifacts and
remaining work. The recipe is experimental and is not ready for redistribution.

Experimental, source-locked build of libmpv at mpv commit
`baa3e11d42cb7978da634a8a6a3a55fe074d01be`. No application source or user media
is included. Nothing here is a release or a certification of legal compliance.

The BtbN tool image is fixed by OCI digest in `sources.lock.json`. Its prebuilt
FFmpeg dependency prefix is made inaccessible before compiling. Runtime libraries
are rebuilt into a new prefix from the hash-locked public source archives.
Compilation runs with network disabled. The link map is retained and checked for
inherited libraries and selected forbidden dependencies.

The intended Windows paths are `vo=gpu`, D3D11/OpenGL, D3D11VA/DXVA2/NVDEC,
WASAPI, exact seeking, frame navigation, reverse playback and still images.
FFmpeg's native codecs/formats, dav1d and zlib are enabled. libass uses the native
DirectWrite font provider. LuaJIT is retained because the `osc=no` option requires
Lua even when OSC itself is disabled. JavaScript, disc support, network-library wrappers,
VapourSynth, sixel and other unused optional components are disabled.
Vulkan remains disabled and is a blocking R5-equivalence issue until restored
or technically justified; it is not treated as an irrelevant feature.
LittleCMS's GPL plugins are disabled; its MIT core is retained.

## Rebuild

On a Linux x64 Docker host, fetch this recipe, run `python3 scripts/sources.py`,
then load and verify the exact locked image and run it with the repository
mounted as `/work`:

```
python3 scripts/load_toolchain.py
docker run --rm --network=none -v "$PWD:/work" -w /work \
  "$(cat dist/evidence/toolchain-reference.txt)" bash scripts/build.sh
```

Use a clean directory for each rebuild. Sources, compiler image, build paths,
timestamp and PE linker timestamp policy are fixed. Reproducibility is an
empirical result only after independent clean builds produce the same DLL hash.
The CI is manual-only, uses standard public hosted runners, has a 90-minute
build timeout and now authorizes only workflow executions 6 and 7, with no rerun.

The Meson iconv preflight runs immediately after source-building libiconv,
before the long dependency chain. It uses the same cross file, static-search
options and exact iconv-resolution snippet inserted into MPV's build definition.
The snippet keeps iconv required and resolves its static archive by explicit
controlled directory. C/C++ links, selected archive hash and PE import evidence
are recorded. The only upstream build-definition patch is recorded as a diff
and hashes; original source archives and all LGPL controls remain unchanged.

The original registry manifest became unavailable during run 4. Its exact OCI
manifest/config had already been preserved. The loader can recover the same
image from the original content-addressed blobs: it verifies the manifest,
config, every compressed and uncompressed layer, Docker image ID and complete
rootfs chain. It does not select `latest` or rebuild a different image. Recovery
still depends on upstream retaining those blobs; their availability is not
guaranteed permanently.

Artifacts include the DLL/headers, notices, original source archives, recipe,
configuration, link map, PE imports and test evidence. `test-tools/ffmpeg.exe`
is a fixture-generation tool, separate from the proposed runtime package.
The Windows CI smoke test uses synthetic MPEG-4/AAC media, software D3D11 and a
null audio output. Native WASAPI and coexistence with PyAV require the separate
Windows probe; the smoke test does not claim these results.

See `REDISTRIBUTION.md` for the evidence boundaries and redistribution material.
Build scripts written for this repository are MIT licensed. Upstream source
archives retain their own licenses; this does not relicense mpv or dependencies.
