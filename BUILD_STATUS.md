# Bounded build evidence

Maximum: three build workflow executions. Manual dispatch only; no reruns.

| Run | Result | Evidence |
| --- | --- | --- |
| 1 | Failed: zimg source snapshot omitted its required graphengine submodule. Preceding libraries compiled. | [40354512350](https://github.com/julianomnunes/libmpv-lgpl-build/actions/runs/40354512350) |

The diagnosed source omission is fixed by locking the gitlink revision
`cb5b2ce13384ec2491f0c37256ea210034799f69` and its archive hash. Other gitlinks
were inspected: libplacebo's required generation/header submodules are locked;
excluded demo/test dependencies are not used. Shaderc's used DEPS revisions are
locked separately. Source acquisition completes before network-isolated build.

Toolchain runtime notices and native Windows/PyAV test environment locks have
been added. MPV's version metadata now records the fixed source revision even
though builds use source archives without a Git worktree. This is the only
source-file edit applied by the recipe.
