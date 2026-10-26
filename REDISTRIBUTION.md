# Redistribution evidence and remaining obligations

This is an engineering evidence package, not legal approval of an application.
Do not redistribute only the DLL while discarding its corresponding source and
notices. Source licenses in the archives include files excluded from this build;
the configuration and link map identify the actual runtime combination.

The selected mpv, libplacebo, FFmpeg, FriBidi and libiconv library sources permit
LGPL-2.1-or-later builds under the selected flags. mpv uses `gpl=false`; FFmpeg
disables GPL, nonfree, version3 and external-library autodetection. FFmpeg uses
native codecs plus dav1d/zlib and header-only nv-codec interfaces. x264/x265,
Chromaprint/FFTW, and LittleCMS's GPL fastfloat/threaded plugins are excluded.

Preserve upstream copyright notices, complete applicable license texts,
disclaimers and any required attribution. FreeType is selected under its FTL:
"Portions of this software are copyright (C) The FreeType Project
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
Those notice materials must be completed and verified against the actual link
map before marking this evidence package ready for redistribution.

GitHub Actions artifacts expire. A future distributor must retain and supply
the source/notice material for the legally required period; a moving upstream
URL or an expiring CI artifact is not a permanent source-delivery arrangement.
