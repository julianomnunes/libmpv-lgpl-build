# Redistribution evidence and remaining obligations

This is an engineering evidence package, not legal approval of an application.
Do not redistribute only the DLL while discarding its corresponding source and
notices. Source licenses in the archives include files excluded from this build;
the configuration and link map identify the actual runtime combination.

The preserved non-Vulkan baseline from clean builds 6/7 is documented in the
history. The current Vulkan candidate is run 8:
libmpv SHA-256 `de35e5b4ebd9c0a2f12033c76479c1653becc83cb81e7ce4612b2354da6cb9e8`,
plus vulkan-1.dll SHA-256 `e24da109c67728423ce11bca10bf2519338b0153b4fc14fbbfb69a9d82cc7d6b`.
[Verification](evidence/run8-build-verification.json) binds the pair to 26
preserved source archives, configuration, final link map and 92 notice files.
Native Vulkan acceptance is blocked and run 9 has not been used. Neither clean
reproduction of this pair nor legal/application distribution approval is claimed.

The intended distribution license of the combined DLL is LGPL-3.0-or-later,
selected from the LGPL-2.1-or-later grants of mpv, libplacebo, FFmpeg, FriBidi
and libiconv. Original source notices are retained. The Apache-2.0 components'
terms also remain applicable. Both LGPLv3 and its underlying GPLv3 text are
supplied; supplying that GPL text is part of LGPLv3 and is not evidence of a
GPL-only runtime dependency. mpv uses `gpl=false`; FFmpeg
disables GPL, nonfree, version3 and external-library autodetection. FFmpeg uses
native codecs plus dav1d/zlib and header-only nv-codec interfaces. x264/x265,
Chromaprint/FFTW, and LittleCMS's GPL fastfloat/threaded plugins are excluded.

Preserve upstream copyright notices, complete applicable license texts,
disclaimers and any required attribution. FreeType is selected under its FTL:
"Portions of this software are copyright (C) 2026 The FreeType Project
(www.freetype.org). All rights reserved."
HarfBuzz, libass, dav1d, zlib, LittleCMS, zimg, shaderc, glslang, SPIRV-Tools,
SPIRV-Headers, SPIRV-Cross and generated-code dependencies retain their upstream
permissive notices. The exact source snapshots and copied notice files are
listed in `source-and-license-manifest.json`; full sources preserve notices
embedded in individual files as well.

Redistribution of this combined DLL requires a supported way to obtain its
complete corresponding library source, changes and build instructions under
the applicable LGPL terms. The source bundle includes original hash-locked
archives and the complete build recipe. Future application packaging must also
preserve replacement/rebuilding of the shared library and the applicable rights
to modify and reverse-engineer for debugging such modifications. Application
license terms and the final packaging arrangement have not been reviewed here.

The build image contains GCC/MinGW tools. Compiler runtime provenance is bound
to that immutable image; GCC runtime libraries use the GCC Runtime Library
Exception and MinGW runtime components have their own permissive notices.
The standard GCC 16.2.0 exception/license texts and MinGW-w64's collected runtime
notices are preserved in `toolchain-notices`, with immutable source URLs and
hashes. Actual compiler/runtime hashes and link map are captured during build.
The image is not rebuilt here; its binary identity is fixed by OCI digest. The
MinGW notice snapshot comes from the BtbN recipe revision preceding that image;
this temporal association alone does not prove a source-to-toolchain rebuild.

GitHub Actions artifacts expire. A future distributor must retain and supply
the source/notice material for the legally required period; a moving upstream
URL or an expiring CI artifact is not a permanent source-delivery arrangement.


Vulkan restoration candidate (runs 8/9): the matching official Khronos
Vulkan-Loader 1.4.345 is built from its locked source, including its bundled
cJSON and Windows directory helper. The loader's Apache-2.0 text and embedded
MIT/permissive copyright/permission notices are copied explicitly and hash
recorded. Both the loader and its exact headers are included in corresponding
sources. The resulting runtime must include the matching vulkan-1.dll alongside
libmpv-2.dll. GPU vendor drivers are system prerequisites, not included binaries.
LGPL/GPL exclusions and the existing legal-review boundaries above still apply.
