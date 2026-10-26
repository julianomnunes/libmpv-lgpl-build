# Bounded build evidence

Maximum: three build workflow executions. Manual dispatch only; no reruns.

| Run | Result | Evidence |
| --- | --- | --- |
| 1 | Failed: zimg source snapshot omitted its required graphengine submodule. Preceding libraries compiled. | [40354512350](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40354512350) |
| 2 | Runtime dependencies and FFmpeg compiled. MPV configuration failed to locate iconv because the explicit linker arguments omitted the new prefix library search path. | [40355969742](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40355969742) |

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
