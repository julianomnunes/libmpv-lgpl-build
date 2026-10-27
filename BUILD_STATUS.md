# Bounded build evidence

Initial runs 1-7 and their evidence are preserved below. Current authorization:
**at most two new first-attempt CI executions, 8 and 9**, no reruns. Run 8
restores Vulkan; run 9 is reserved for a clean reproduction or a specifically
diagnosed correction. Manual dispatch only.

Current state: **run 8 passed build and Windows smoke (52 checks)** and
produced libmpv + the matching Vulkan loader. Vulkan/D3D11/iconv are enabled;
all LGPL exclusions pass. Native D3D11/WASAPI and both PyAV orders passed.
**Native Vulkan stalls during the first frame and remains blocking.**
Bounded investigation found a driver/OBS-hook wait; exact cause is not proved.
Work stopped at this substantial runtime-validation blocker. Run 9 is unused;
no rerun, clean Vulkan reproduction or integration approval is claimed.

| Run | Result | Evidence |
| --- | --- | --- |
| 1 | Failed: zimg source snapshot omitted its required graphengine submodule. Preceding libraries compiled. | [40354512350](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40354512350) |
| 2 | Runtime dependencies and FFmpeg compiled. MPV configuration failed to locate iconv because the explicit linker arguments omitted the new prefix library search path. | [40355969742](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40355969742) |
| 3 | The early iconv C++ link check passed. LuaJIT's Linux host/minilua link inherited the Windows-only `--no-insert-timestamp` flag and failed. No DLL was produced. | [40360933569](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40360933569) |
| 4 | Source hashes passed; the registry returned `manifest unknown` for the original fixed tool image. Compilation did not start, so the LuaJIT correction was not exercised. | [40366278253](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40366278253) |
| 5 | Exact image recovered and verified; initial LuaJIT ELF/COFF preflight passed; dependencies and FFmpeg compiled. MPV still failed at static iconv discovery. No DLL; Windows job skipped. | [40367529330](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40367529330) |
| 6 | Build passed, including the initial static iconv preflight and final static link. Windows smoke failed at raw EOF back-step; the identical failure was reproduced with R5. DLL and both artifacts preserved and verified; corrected local smoke passed without rebuilding. | [40378862793](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40378862793) |
| 7 | Clean build and corrected Windows smoke passed (50 checks). DLL, FFmpeg tool, runtime manifest, link map and source/license manifest are byte-identical to build 6. Vulkan remains absent and blocking. | [40401417585](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40401417585) |
| 8 | Build, initial Vulkan/Meson preflight and Windows smoke passed (52 checks). Native D3D11/PyAV passed; forced Vulkan stalled even with software decoding. DLL pair and complete sources/notices preserved. Run 9 not dispatched. | [40419014102](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40419014102) |

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


## Run 6: produced DLL, diagnosed Windows harness failure

The DLL SHA-256 is
`0eda750efb1b71136f66bf5acd74370bcb27f99ef0b14dffef0ae62700e0ecc1`.
[Build verification](evidence/run6-build-verification.json) records its size,
all runtime-file hashes, the 25 verified source archives, actual linked static
archives, PE imports and excluded GPL dependencies. Static iconv remained
required and enabled; its early Meson preflight and final MPV link both passed.

- [Build artifact 6](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40378862793/artifacts/12678429164): SHA-256 `aaaf2fe8998dd333a9be11c0851eda54c2e0e87b49ab45b697c1a71a4657f02d`.
- [Original failing smoke 6](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40378862793/artifacts/12679835813): SHA-256 `ff08f817c392099d498465485eaa37624388a1b0ab51da63820a60b4462c2af3`.

The failing assertion demanded a raw `frame-back-step` immediately after EOF.
Both this DLL and R5 remain at 4.966667 s on the exact preserved MPEG-4/AAC
fixture. This is documented behavior of the test scenario, not a newly proven
library regression. The application already intercepts EOF navigation: pause,
forward direction, safe exact seek two seconds before the last decoded PTS,
stable non-EOF observations, then exact seek inside the penultimate frame.
Reverse at EOF starts through controlled frame commands; switching directly to
native reverse there stalls with both DLLs. The probe now verifies that actual
C-API protocol, requiring the penultimate PTS, clear EOF, stable seek and six
successful backward frames. It does not import or publish application code.
The synthetic CI fallback explicitly requires the known 150-frame/30-fps fixture;
PyAV runs use real decoded tail PTS. Ordinary frame stepping and native reverse
away from EOF remain required checks. The host HWND now runs a dedicated Windows
message loop instead of leaving the embedding window unserviced.

Before run 7, the corrected probe passed with the preserved DLL on the CI
fixture, and on H.264/AAC with WASAPI, D3D11VA and PyAV loaded before/after
libmpv. Metadata, audio samples and decoded EOF frames passed, with three core
FFmpeg DLL runtime license checks and actual module hashes. No x264/x265 DLLs
were loaded. The corresponding R5 corrected EOF smoke also passed. These are
isolated C-API checks, not a full GUI regression or an audible/visual acceptance.

The OpenGL/NVDEC variant stalls in native reverse at 3 s with both R5 and this
DLL; that path is not approved. The new DLL rejects Vulkan as compiled; a
D3D11/default pass does not replace that missing fallback. Vulkan remains
blocking until restored or adequately justified. The build recipe, dependency
locks and compiler options are unchanged for run 7: it will be a fresh compile
plus the corrected smoke, not a rerun of run 6, to compare the exact DLL hashes.


## Final result after run 7 — budget exhausted

[Reproducibility evidence](evidence/run6-run7-reproducibility.json) verifies
byte-for-byte equality of the two DLLs, not only equal reported versions:
55,753,216 bytes, SHA-256
`0eda750efb1b71136f66bf5acd74370bcb27f99ef0b14dffef0ae62700e0ecc1`.
Both jobs built a fresh prefix from the 25 hash-locked archives, without network
during compilation, using the same recovered OCI image. The compiler runtime
hashes, source/license manifest, link map, build configuration, iconv preflight,
FFmpeg fixture tool and complete runtime SHA256SUMS also match. Documentation
and the corrected test probe changed, so the corresponding-source bundle and
artifact ZIP hashes differ as expected; no whole-ZIP reproducibility is claimed.

- [Build 7 DLL, sources and notices](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40401417585/artifacts/12690831723): SHA-256 `bc90ca6313e853ee30e97fb3ecdb096e9590c197c35fc9ac3754238cb9e0eb23`.
- [Windows smoke 7](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40401417585/artifacts/12690840825): SHA-256 `07ab3b5c5e1063eead3ac2777f163253d45aec0752d0260481ea2fbb569831a0`.
- Build 7 corresponding-source tarball: SHA-256 `1f111a4752d2b7ebf20801d7c5c04fcf045ddf614c2264c5740fb953711df555`.

[Windows CI report](evidence/run7-windows-smoke.json) passed all 50 checks with
software D3D11/WARP and null audio on Windows 2025/Python 3.12. Native isolated
Windows/Python 3.14.7 checks used the **same verified DLL hash**:
[summary](evidence/run6-native-summary.json),
[PyAV first](evidence/run6-native-wasapi-pyav-first.json),
[PyAV last](evidence/run6-native-wasapi-pyav-last.json).
Playback, WASAPI initialization, pause, exact/keyframe seeks, frame steps,
native reverse away from EOF, safe-seek recovery to the penultimate PTS,
controlled reverse frames after EOF and PNG capture/load passed on D3D11.
PyAV 18.1.0/FFmpeg 9.0.2 LGPL read metadata, decoded 240,000 audio samples and
recovered the last video PTS (4.966667 s). The seven loaded FFmpeg DLLs have
the approved environment's hashes; core runtime license APIs report LGPLv3+,
and no x264/x265 DLL was loaded. libmpv's FFmpeg is linked internally rather
than resolving those PyAV DLLs. These results are reused by byte identity,
without a redundant native replay of build 7.

The native default path was D3D11/D3D11VA for both the candidate and R5. The
OpenGL/NVDEC reverse test stalled at 3 s in both DLLs; it remains a recorded
limitation, not a passed path. The R5 Vulkan probe exceeded the isolated
75-second limit even with a serviced host HWND:
[timeout record](evidence/run6-native-r5-vulkan-timeout.json). That result is
inconclusive and does not justify deleting Vulkan. The candidate explicitly
rejects Vulkan and records HAVE_VULKAN=0. Source confirms that its omission
removes a Windows fallback after D3D11. **R5 equivalence is therefore not
approved.** Restoring it requires enabling Vulkan in libplacebo and MPV,
supplying a traceable Vulkan loader/import dependency (MPV requires >=1.4.309),
recording its notices, and validating that revised DLL and clean reproduction.
No such build is authorized or started. These probes also do not establish
audible synchronization, visual acceptance or a full application regression.

Licensing engineering checks passed for the produced bytes: MPV GPL disabled,
FFmpeg GPL/nonfree/version3 disabled, required static iconv present, no forbidden
GPL/inherited archive in the link map, all 25 original source archives verified,
and 88 notice files preserved. The map records the actually extracted archive
members separately from link inputs. The intended combined grant is LGPLv3+;
original component notices and obligations remain. As detailed in
[REDISTRIBUTION.md](REDISTRIBUTION.md), durable source delivery, final application
terms/library replacement rights and exact MinGW runtime notice/source
association remain to be settled. The compiler image and runtime bytes are
fixed, but the temporal MinGW source association is not proof of rebuilding
that toolchain. Its legal significance needs review; no legal approval is inferred.

[CI ledger](evidence/final-ci-runs.json): exactly seven runs, all attempt 1;
run 7 took 26 min 48 s including smoke. The workflow only permits builds 6/7
and rejects reruns. Both downloaded ZIP pairs and extracted DLL/source/log
evidence remain outside the application checkout. [Preservation check](evidence/original-preservation-final.json)
confirmed all seven original fingerprints and the preexisting Git status
unchanged, including the crash report and R5. No application code/private media
was uploaded; no application integration, release or 11E work was performed.


## Authorized Vulkan continuation: runs 8 and 9

Vulkan-Headers 1.4.345 remains at the already locked commit
74d8a6cb930c68ef617b202c3ff3c59d919e086b. The matching official Khronos
Vulkan-Loader tag v1.4.345 resolves to commit
363f465abadab0a8dcfc5c85d2c691e9b0b788d6; its source archive SHA-256 is
46787c41f03c90949a5262eb0eaaca79214829eb59b61c38f7890adb32ea70f8.
Its known_good.json requests exactly the same header version. Production builds
use only those headers plus Windows system libraries; googletest/Detours are
excluded test dependencies. The Apache-2.0 license and embedded cJSON MIT and
Kevlin Henney directory-code notices are preserved explicitly, with hashes.
No existing source revision or toolchain image is changed.

The loader is built early with MinGW GAS trampolines required, before iconv,
shaderc and FFmpeg. Automatic dependency downloads, tests, code regeneration
and unsafe loader searches are off. A minimal C/Meson link uses MPV's same
prefer_static/default_library options, requires Vulkan >=1.4.309 and exact
header patch 345, and records the controlled import archive and PE import.
The Vulkan loader is necessarily a shared Windows library; both vulkan-1.dll
and libmpv-2.dll are part of the candidate runtime. This explicit Apache-licensed
shared dependency does not relax any LGPL/GPL controls. libplacebo Vulkan and
vk-proc-addr, plus MPV Vulkan, are required enabled; D3D11 and iconv stay required.
FFmpeg's approved configuration is unchanged, including its Vulkan hardware
codecs/filters remaining disabled; this restoration concerns MPV's graphics
backend and preserves its existing D3D11VA/DXVA2/NVDEC paths.

Essential validation only: existing Windows D3D11/WARP smoke, native default
D3D11/WASAPI plus both approved PyAV load orders, and a forced Vulkan synthetic
playback/navigation probe. The probe verifies the actually loaded bundled
loader path/hash/API version and the selected graphics context. A visible,
non-activating host and engine log are available for that Vulkan probe.
A single pre-CI check with R5 still blocked during first-frame presentation
with H.264/NVDEC, despite the serviced visible host; its log established Vulkan
device creation and successful shader/pipeline creation before the stall.
This is a preexisting test-path limitation, not evidence that the new DLL
works or fails. Candidate validation may isolate software decoding if the same
specific interop problem is observed. No HDR/visual/opening stress battery or
application execution is planned.


## Result after run 8: Vulkan compiled; native acceptance blocked

The [verified build](evidence/run8-build-verification.json) produced this required
pair, from unchanged MPV baa3e11d and the locked Khronos 1.4.345 loader/headers:

| Runtime file | SHA-256 |
| --- | --- |
| libmpv-2.dll | de35e5b4ebd9c0a2f12033c76479c1653becc83cb81e7ce4612b2354da6cb9e8 |
| vulkan-1.dll | e24da109c67728423ce11bca10bf2519338b0153b4fc14fbbfb69a9d82cc7d6b |

[Full build artifact](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40419014102/artifacts/12698500080),
145,313,631 bytes, SHA-256
`603adc89bd2ff486e7991c99cf3a1c1466be0ad6afc755d0dcb847f7a887ee02`.
It includes both DLLs, headers/import library, recipe, link map, PE imports,
26 verified source archives and 92 notice files, including all three embedded
loader notices. The corresponding-source tarball SHA-256 is
`ec45c1ccf0151db40e44690ee966faac1e89c7a9896cebf61b28bbdae1a6ea4f`.
MPV HAVE_VULKAN/HAVE_D3D11/HAVE_ICONV are 1; HAVE_GPL is 0. FFmpeg
GPL/nonfree/version3 stay 0; its native Vulkan hardware contexts remain off.
The supported hwcontext stub permits graphics Vulkan without enabling those
extra codecs/filters. No forbidden or inherited archive appears in the map.
The helper FFmpeg and client import library hashes still match builds 6/7.

[Windows smoke artifact](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40419014102/artifacts/12696929692),
SHA-256 `d4f0d5c8ced7b54f1f1fe66c8baff8922235c783f22d4c83ac71516dce8390ab`:
[all 52 checks passed](evidence/run8-windows-smoke.json) using WARP.
Native Python 3.14.7/PyAV 18.1.0/FFmpeg 9.0.2 LGPL passed
[D3D11/PyAV first (61 checks)](evidence/run8-native-d3d11-pyav-first.json) and
[default/PyAV last (58 checks)](evidence/run8-native-default-pyav-last.json).
The default remains vo=gpu/D3D11/D3D11VA; WASAPI, playback, pause, seeks,
frame steps, reverse/EOF recovery and PNG preview passed. All three PyAV
operations and actual module hashes passed, without x264/x265. The actual
bundled loader identity was checked; its API reports 1.4.345.

The [native summary](evidence/run8-native-summary.json) preserves the failed
forced-Vulkan test: first-frame rendering stalled after successful Vulkan
device, shader and pipeline creation, even with software video decoding.
No transport/preview pass on Vulkan is inferred. A single
[Frida thread snapshot](evidence/run8-vulkan-thread-diagnosis.json) shows the
render path waiting inside the NVIDIA driver with OBS graphics-hook64.dll
interposed. Stripped-module symbol labels are approximate; this observation
does not establish OBS as the sole cause or prove a library defect. R5 had
also stalled in a comparable forced-Vulkan probe.

Only child-process environment filters were tried, using the installed OBS
manifest and the official loader's documented implicit-layer filter. Elevated
execution can ignore those variables. A linked standard-user token was
unavailable (WinError 1312); a restricted-token launcher failed before starting
a child. A disposable helper was then reduced to verified medium integrity,
but its Vulkan child still timed out. No OBS service, driver, UAC, account,
registry, application option or global environment was changed. These bounded
diagnostics did not establish a corrective build change. **Vulkan runtime
acceptance and R5 equivalence remain blocked.**

Run 9 is deliberately unused: recompiling the same sources would not resolve
this first-frame block, and a clean reproduction is secondary to functionality.
The minimum next step is to exercise this existing DLL pair in a clean,
non-elevated Windows session without injected capture layers, before any new
build. If that passes, the remaining authorized run 9 could reproduce the
unchanged recipe (about 28 minutes based on run 8). Otherwise the driver/hook/
renderer interaction requires a separately scoped diagnosis; no speculative
patch or LGPL relaxation was made.

For future integration, the candidate requires **both** DLLs adjacent, with the
loader actually resolved from that bundle; vo=gpu/D3D11 and the approved PyAV
stack stay unchanged. No such integration is authorized or performed here.
The source/notice chain is recorded, but the existing MinGW source association,
durable source delivery and final application LGPL terms still require review;
no legal certification follows from these engineering checks.

[Preservation evidence](evidence/run8-preservation.json) confirms the original
checkout/R5 and all seven fingerprints and preexisting Git changes unchanged.
The CI ledger has eight runs, all attempt 1. No release or 11E work was started.
The delivered run 8 package is explicitly a **candidate with native Vulkan
acceptance blocked**, not a ready-to-integrate or redistributability approval.

Local handoff: `libmpv-lgpl-vulkan-run8-candidate.zip`, with the full source/notice
package plus current evidence. [Delivery hash/content manifest](evidence/run8-delivery.json).
It is labelled candidate/blocked and is not a published release.
