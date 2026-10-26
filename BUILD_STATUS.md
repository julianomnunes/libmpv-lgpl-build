# Bounded build evidence

Initial budget: three executions, followed by the completed authorization for
runs 4 and 5. Current authorization: **at most two new executions, 6 and 7**, no
reruns. Manual dispatch only. All previous attempt records below are preserved.

Current state: no DLL yet. The run 6 static iconv correction and matching Meson
preflight are prepared. LuaJIT host/target separation and exact image recovery
are already verified. Windows tests and practical Vulkan comparison remain
unexecuted; Vulkan is still an impediment to R5-equivalence approval.

| Run | Result | Evidence |
| --- | --- | --- |
| 1 | Failed: zimg source snapshot omitted its required graphengine submodule. Preceding libraries compiled. | [40354512350](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40354512350) |
| 2 | Runtime dependencies and FFmpeg compiled. MPV configuration failed to locate iconv because the explicit linker arguments omitted the new prefix library search path. | [40355969742](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40355969742) |
| 3 | The early iconv C++ link check passed. LuaJIT's Linux host/minilua link inherited the Windows-only `--no-insert-timestamp` flag and failed. No DLL was produced. | [40360933569](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40360933569) |
| 4 | Source hashes passed; the registry returned `manifest unknown` for the original fixed tool image. Compilation did not start, so the LuaJIT correction was not exercised. | [40366278253](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40366278253) |
| 5 | Exact image recovered and verified; initial LuaJIT ELF/COFF preflight passed; dependencies and FFmpeg compiled. MPV still failed at static iconv discovery. No DLL; Windows job skipped. | [40367529330](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40367529330) |

The diagnosed source omission is fixed by locking the gitlink revision
`cb5b2ce13384ec2491f0c37256ea210034799f69` and its archive hash. Other gitlinks
were inspected: libplacebo's required generation/header submodules are locked;
excluded demo/test dependencies are not used. Shaderc's used DEPS revisions are
locked separately. Source acquisition completes before network-isolated build.

Toolchain runtime notices and native Windows/PyAV test environment locks have
been added. MPV's version metadata now records the fixed source revision even
though builds use source archives without a Git worktree. This is the only
source-file edit applied by the recipe.

Before run 3, the diagnosed library-search omission is corrected by retaining
the full controlled LDFLAGS in MPV's explicit linker arguments. The successful
iconv detection in libass's Meson log used `-L/work/prefix/lib`; the failed MPV
probe omitted it. A small C++ iconv link probe now fails early if this recurs.
Source review also found two compatibility/license issues: `osc=no` requires
Lua, so the matching pinned LuaJIT revision is restored; legacy `direct3d` is
GPL-only and is disabled while modern D3D11 remains enabled. No application
option is changed. The PC metadata version of SPIRV-Cross is derived from its
actual source instead of a placeholder. Run 3 is the final allowed execution.

## Initial stop after run 3 and exact remaining work

Budget exhausted: **3/3 executions**, no reruns, no release, no application
integration. No successful libmpv artifact or binary reproducibility result.

The final failure is in the recipe's separation of Linux host-tool and Windows
target flags. LuaJIT's `src/Makefile:192` defines `LDOPTIONS` using generic
`LDFLAGS`, and `HOST_ALDFLAGS` incorporates it. The Linux linker rejects the PE
timestamp option at `host/minilua`. A localized next correction is to pass empty
generic `LDFLAGS` to this make invocation and put the Windows flags into
`TARGET_LDFLAGS` (and target shared flags if used). No fourth execution was
started and this proposed correction has not been compiled or validated.

At least one further successful build and native Windows tests are needed for a
functional candidate. Run 2's complete dependency/FFmpeg compilation took about
25 minutes on the standard runner. A separate successful clean rebuild would
then be needed to demonstrate bit-for-bit DLL reproducibility. Additional
errors beyond the current failure remain possible because the final DLL link
has never completed.

The isolated test environment was installed from the public explicit lock:
Python 3.14.7, av 18.1.0 `py314hc59ccdc_1`, FFmpeg 9.0.2
`lgpl_haba0ffa_805`. [Environment evidence](evidence/pyav-environment.json)
records the seven actually loaded FFmpeg DLL hashes, their LGPLv3-or-later
runtime declarations, `--disable-gpl` configurations and absence of x264/x265/
FFTW packages and DLLs. This validates the test environment only. Playback,
WASAPI, pause, seek/scrub, stepping, reverse/EOF, preview and coexistence with the
new libmpv were **not run** because no new DLL exists.

Diagnostic artifacts (no redistributable runtime DLL):

- [Build 2 diagnostics](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40355969742/artifacts/12668290091), SHA-256 `a14a518e2ecdd352f3bef989cda2817327e8bf2b11b25459d8db522a9caccd5f`.
- [Build 3 diagnostics](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40360933569/artifacts/12666469915), SHA-256 `4faf6274b49c27594ae19d4b043b17748c4fc7166d7269d2973dfee325e607ba`.

Sources and primary notices are locked and preserved, but conformity of an exact
new DLL cannot be asserted without that binary, its completed link evidence and
the remaining checks. The existing approved binary's status is not changed by
this failed experiment.

## Authorized continuation: runs 4 and 5

The reviewed correction leaves generic `LDFLAGS`, `HOST_LDFLAGS` and
`HOST_XLDFLAGS` empty for the LuaJIT make invocation. Windows flags are passed
only through `TARGET_LDFLAGS` and `TARGET_SHLDFLAGS`, which feed the target link
rules rather than `host/minilua`. Host C flags and target C flags remain
separate. This follows the exact rules of the pinned LuaJIT Makefile, not a
change to its source. The shell recipe is syntax-checked before dispatch.

LuaJIT now builds before zlib/iconv and the long dependency/FFmpeg chain. The
initial stage verifies the Linux ELF host tool, the Windows x64 COFF object,
and the installed static archive, retaining hashes and format evidence. Run 4
is dispatched only after reviewing this correction. Run 5 is reserved for a
clean reproduction or a newly diagnosed blocker; a sixth run and all reruns
are outside authorization.

Vulkan remains disabled in this candidate. Source review at MPV `baa3e11d`
shows Windows `vo=gpu` auto-probing D3D11 first, then Vulkan, then OpenGL
(`video/out/gpu/context.c`). Omitting Vulkan therefore removes an available
fallback; it does not establish equivalence to R5. If a DLL is produced, native
Windows tests must record actual selected graphics/hardware-decoding paths,
exercise the required functions and compare the available paths with the R5
configuration before drawing a scoped conclusion.

Run 4's environmental blocker is addressed without changing the toolchain:
the exact OCI manifest (SHA-256 `59662fba...`) and config (image ID
`sha256:bcb2595e1c9698573daaee97cf871954334f4d9d01b1fb419291b4759b44d3e3`)
were saved before the manifest disappeared. All 17 original compressed blobs
(2,067,025,173 bytes) were checked available with exact Content-Length before
run 5; see [preflight evidence](evidence/toolchain-recovery-preflight.json).
The recovery loader verifies both compressed blob hashes and the uncompressed
rootfs diff IDs, then requires Docker to report that same image ID/rootfs chain.
Docker archive layout and compressed-layer loading were checked against Moby
`v28.3.3`, `image/tarexport/load.go`. The OCI metadata is preserved byte-for-byte.
No replacement image, new dependency revision or extra build execution is used.
Only run 5 remains authorized. Upstream blob retention remains an availability
limitation even if recovery succeeds.

## Result after authorized run 5

The LuaJIT correction is verified by [preflight evidence](evidence/run5-luajit-preflight.json):
Linux ELF host/minilua and Windows x64 COFF target object were produced before
other dependencies. The installed static archive SHA-256 is
`79c4827b93399d8c9ee79ac00d6231297b521173b88bcb4aeb64948355f9e5c7`.
[Recovery evidence](evidence/run5-toolchain-recovery.json) verifies all 17
compressed and uncompressed layer hashes and the original Docker image/rootfs
identity. There was no toolchain-version substitution.

The remaining iconv failure is more specific than a missing `-L`: the explicit
C++ link probe passes, libass's iconv detection passes, and MPV's command now
contains `-L/work/prefix/lib`. Under `--prefer-static`, however, Meson 1.12.1's
`IconvSystemDependency` calls `find_library` without extra directories; its
static search uses the compiler's reported library directories, which omit the
controlled prefix. The fast `-liconv` linker probe is used only for
`PREFER_SHARED`. [Diagnostic excerpt and source references](evidence/run5-iconv-diagnosis.txt)
show this distinction. The previous linker-path correction was insufficient.
Any future correction must expose the controlled archive/directory explicitly
to Meson's static dependency discovery, then be compiled and tested. No such
additional correction or sixth build was attempted in this budget.

[Run 5 diagnostic artifact](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40367529330/artifacts/12671938247),
583,536 bytes, verified SHA-256
`215fe6711b9c9fab21deecc7935b583a213faab1bbac4bcff1a97fab87dbf109`.
It contains logs, source/license manifests, notices, toolchain and LuaJIT
evidence, and FFmpeg configuration; it contains no redistributable libmpv DLL.
FFmpeg's recorded GPL/nonfree/version3 flags are zero. There is no completed
final link map, DLL hash or clean DLL reproduction to validate.

The graphics probe now supports explicit API/context selection and records
`current-gpu-context`; it was syntax-checked but not executed. Vulkan's omission
removes a fallback in the pinned source's D3D11 -> Vulkan -> OpenGL selection
order. Its practical effect versus R5, and the full required Windows operations
and PyAV coexistence, remain untested because no candidate DLL exists. No
functional-equivalence or legal-conformity conclusion follows from this run.

The Roteirizador checkout, its preexisting local changes, crash report and R5
executable/native DLLs were preserved; recorded file fingerprints were compared
unchanged at the end. Only the isolated build repository was updated. No release,
integration or 11E work was performed. Exactly five first-attempt workflow runs
exist; no reruns or further execution were requested.

## Authorized continuation: runs 6 and 7

The iconv correction preserves `iconv=enabled`, `static: true`, MPV `gpl=false`
and all FFmpeg GPL/nonfree exclusions. A single shared Meson snippet uses
`cc.find_library('iconv', dirs: [prefix/libdir], static: true, required: iconv)`.
It is evaluated by the preflight and inserted in place of MPV's diagnosed
directory-less iconv discovery. The patcher verifies the exact original Meson
file hash and records a minimal diff plus original/patched hashes. No runtime
source is changed and no binary library is substituted.

Immediately after source-installing iconv, before zlib and the long dependency
chain, the minimal Meson project uses the same cross file, prefix/libdir,
`default_library=shared`, `prefer_static=true`, `wrap_mode=nodownload`,
`auto_features=disabled`, `iconv=enabled` and linker options as MPV. It requires
the header and builds C/C++ clients. Recorded Ninja commands must select the
controlled `libiconv.a`; import archives and iconv DLL imports are rejected.
The real MPV configuration must still report `HAVE_ICONV=1` and its final link
map must include that static archive. Run 6 follows review/syntax checks; run 7
is reserved for a clean reproduction if run 6 passes, otherwise a concretely
diagnosed correction. No reruns or eighth execution are authorized.

Vulkan remains disabled and explicitly blocking. A successful non-Vulkan DLL
or a local default-backend pass alone does not close R5 equivalence. It must be
restored or supported by an adequate technical justification. No such closure
is claimed in this continuation's preparation.
