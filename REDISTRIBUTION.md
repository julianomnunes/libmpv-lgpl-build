# Redistribution evidence and remaining obligations

This is an engineering evidence package, not legal approval of an application.
Do not redistribute only the DLL while discarding its corresponding source and
notices. Source licenses in the archives include files excluded from this build;
the configuration and link map identify the actual runtime combination.

The exact candidate DLL is now reproduced byte-for-byte by clean builds 6/7:
SHA-256 `0eda750efb1b71136f66bf5acd74370bcb27f99ef0b14dffef0ae62700e0ecc1`.
[Verification](evidence/run6-run7-reproducibility.json) binds those bytes to the
25 preserved source archives, build configuration, final archive-member/link
map and source/license manifest. It verifies the GPL exclusions technically;
it does not approve an application's legal terms or final distribution.

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
