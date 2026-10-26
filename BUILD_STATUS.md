# Bounded build evidence

Initial budget: three build workflow executions. Authorized continuation:
**at most two additional executions, numbered 4 and 5**. Manual dispatch only;
no reruns. The original attempt records below are preserved.

| Run | Result | Evidence |
| --- | --- | --- |
| 1 | Failed: zimg source snapshot omitted its required graphengine submodule. Preceding libraries compiled. | [40354512350](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40354512350) |
| 2 | Runtime dependencies and FFmpeg compiled. MPV configuration failed to locate iconv because the explicit linker arguments omitted the new prefix library search path. | [40355969742](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40355969742) |
| 3 | The early iconv C++ link check passed. LuaJIT's Linux host/minilua link inherited the Windows-only `--no-insert-timestamp` flag and failed. No DLL was produced. | [40360933569](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40360933569) |
| 4 | Source hashes passed; the registry returned `manifest unknown` for the original fixed tool image. Compilation did not start, so the LuaJIT correction was not exercised. | [40366278253](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40366278253) |

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
