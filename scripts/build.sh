#!/usr/bin/env bash
set -euo pipefail
cd /work
mkdir -p dist/evidence dist/notices builds prefix
exec > >(tee dist/evidence/build.log) 2>&1
trap 'find builds -name meson-log.txt -o -name config.log | while read -r f; do mkdir -p "dist/evidence/$(dirname "$f")"; cp "$f" "dist/evidence/$f"; done' EXIT

# The pinned upstream image supplies tools only. Its prebuilt FFmpeg libraries
# must never enter this link. /work/prefix starts empty in each clean job.
if [[ -d /opt/ffbuild ]]; then mv /opt/ffbuild /opt/upstream-libraries-disabled; fi
export SOURCE_DATE_EPOCH=1792881153 TZ=UTC LC_ALL=C
export CC=x86_64-w64-mingw32-gcc CXX=x86_64-w64-mingw32-g++
export AR=x86_64-w64-mingw32-gcc-ar RANLIB=x86_64-w64-mingw32-gcc-ranlib
export NM=x86_64-w64-mingw32-gcc-nm STRIP=x86_64-w64-mingw32-strip
export PREFIX=/work/prefix
export PKG_CONFIG_LIBDIR="$PREFIX/lib/pkgconfig:$PREFIX/share/pkgconfig"
export PKG_CONFIG_PATH= PKG_CONFIG_SYSROOT_DIR=
export CFLAGS="-O2 -g0 -I$PREFIX/include -ffile-prefix-map=/work=. -fno-ident"
export CXXFLAGS="$CFLAGS"
export LDFLAGS="-L$PREFIX/lib -static-libgcc -static-libstdc++ -Wl,--no-insert-timestamp"
export CPPFLAGS="-I$PREFIX/include"
export LIBRARY_PATH="$PREFIX/lib"
unset FF_CONFIGURE FF_CFLAGS FF_CXXFLAGS FF_LIBS FF_LDFLAGS FF_LDEXEFLAGS
JOBS=4
{ "$CC" -v; "$CXX" -v; meson --version; cmake --version; ninja --version; nasm -v; } > dist/evidence/tool-versions.txt 2>&1
cp sources.lock.json dist/
cp -r toolchain-notices dist/notices/compiler-runtime
cp upstream-origin.json dist/evidence/
for runtime in libgcc.a libgcc_eh.a libstdc++.a libwinpthread.a libmingwex.a libmingw32.a crtbegin.o crtend.o; do
  path=$("$CC" -print-file-name="$runtime")
  if [[ -f "$path" ]]; then sha256sum "$path"; else echo "$runtime: not found"; fi
done > dist/evidence/compiler-runtime-hashes.txt
cp /cross.meson /toolchain.cmake dist/evidence/
cp scripts/cross.meson scripts/toolchain.cmake dist/evidence/

python3 scripts/sources.py
python3 scripts/sources.py --collect

meson_static() {
    local name=$1; shift
    meson setup "builds/$name" "sources/$name" --cross-file scripts/cross.meson \
      --prefix="$PREFIX" --libdir=lib --buildtype=release --default-library=static \
      --wrap-mode=nodownload --auto-features=disabled "$@"
    meson compile -C "builds/$name" -j "$JOBS"
    meson install -C "builds/$name"
}
cmake_static() {
    local name=$1; shift
    cmake -S "sources/$name" -B "builds/$name" -GNinja \
      -DCMAKE_TOOLCHAIN_FILE=/work/scripts/toolchain.cmake \
      -DCMAKE_INSTALL_PREFIX="$PREFIX" -DCMAKE_INSTALL_LIBDIR=lib \
      -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF "$@"
    cmake --build "builds/$name" -j "$JOBS"
    cmake --install "builds/$name"
}

(cd sources/zlib && CHOST=x86_64-w64-mingw32 ./configure --static --prefix="$PREFIX" && make -j"$JOBS" && make install)
(cd builds && mkdir iconv && cd iconv && ../../sources/libiconv/configure \
  --prefix="$PREFIX" --host=x86_64-w64-mingw32 --disable-shared --enable-static --disable-nls && make -j"$JOBS" && make install)
cat > dist/evidence/iconv-link-probe.c <<'EOF'
#include <iconv.h>
int main(void) { return iconv_open("UTF-8", "UTF-8") == (iconv_t)-1; }
EOF
"$CXX" $CXXFLAGS $LDFLAGS dist/evidence/iconv-link-probe.c -liconv -o builds/iconv-link-probe.exe
make -C sources/ffnvcodec PREFIX="$PREFIX" install
(cd sources/luajit && sed -i '/^Libs.private/d' etc/luajit.pc && \
  make TARGET_SYS=Windows PREFIX="$PREFIX" HOST_CC=gcc CFLAGS='-O2 -pipe' \
  CROSS=x86_64-w64-mingw32- TARGET_CFLAGS="$CFLAGS" BUILDMODE=static \
  XCFLAGS=-DLUAJIT_ENABLE_LUA52COMPAT FILE_T=luajit.exe INSTALL_DEP=src/luajit.exe amalg install)
meson_static dav1d -Denable_tools=false -Denable_tests=false -Denable_examples=false -Denable_docs=false -Denable_asm=true
cmake_static freetype -DFT_DISABLE_ZLIB=TRUE -DFT_DISABLE_BZIP2=TRUE -DFT_DISABLE_PNG=TRUE -DFT_DISABLE_HARFBUZZ=TRUE -DFT_DISABLE_BROTLI=TRUE
meson_static fribidi -Dbin=false -Ddocs=false -Dtests=false
sed -i 's/Cflags:/Cflags: -DFRIBIDI_LIB_STATIC/' "$PREFIX/lib/pkgconfig/fribidi.pc"
meson_static harfbuzz -Dfreetype=enabled -Dglib=disabled -Dgobject=disabled -Dcairo=disabled \
  -Dchafa=disabled -Dtests=disabled -Dintrospection=disabled -Ddocs=disabled -Dutilities=disabled \
  -Dgpu=disabled -Dgpu_demo=disabled -Draster=disabled -Dvector=disabled -Dsubset=disabled -Dgdi=enabled
meson_static libass -Dtest=disabled -Dcompare=disabled -Dprofile=disabled -Dfuzz=disabled \
  -Dcheckasm=disabled -Dfontconfig=disabled -Ddirectwrite=enabled -Dlibunibreak=disabled -Dasm=enabled
# LittleCMS's fastfloat/threaded plugins are GPL; the MIT core is sufficient.
meson_static lcms2 -Dtests=disabled -Dutils=false -Dfastfloat=false -Dthreaded=false
(cd sources/zimg && ./autogen.sh && ./configure --host=x86_64-w64-mingw32 --prefix="$PREFIX" --disable-shared --enable-static && make -j"$JOBS" && make install)

cmake_static shaderc -DSHADERC_SKIP_TESTS=ON -DSHADERC_SKIP_EXAMPLES=ON \
  -DSHADERC_SKIP_COPYRIGHT_CHECK=ON -DENABLE_GLSLANG_BINARIES=OFF \
  -DSPIRV_SKIP_EXECUTABLES=ON -DSPIRV_SKIP_TESTS=ON -DSPIRV_TOOLS_BUILD_STATIC=ON \
  -DENABLE_EXCEPTIONS=ON
cp builds/shaderc/libshaderc_util/libshaderc_util.a "$PREFIX/lib/"
printf '\nLibs.private: -lstdc++ -lpthread\n' >> "$PREFIX/lib/pkgconfig/shaderc_combined.pc"
cp "$PREFIX/lib/pkgconfig/shaderc_combined.pc" "$PREFIX/lib/pkgconfig/shaderc.pc"

cmake_static spirv-cross -DSPIRV_CROSS_SHARED=OFF -DSPIRV_CROSS_STATIC=ON \
  -DSPIRV_CROSS_CLI=OFF -DSPIRV_CROSS_ENABLE_TESTS=OFF -DSPIRV_CROSS_ENABLE_CPP=OFF
SPIRV_VERSION=$(python3 -c 'import re; from pathlib import Path; s=Path("sources/spirv-cross/CMakeLists.txt").read_text(); print(".".join(re.search(r"set\(spirv-cross-abi-"+v+r" ([0-9]+)\)",s)[1] for v in ("major","minor","patch")))')
cat > "$PREFIX/lib/pkgconfig/spirv-cross-c-shared.pc" <<EOF
prefix=$PREFIX
libdir=\${prefix}/lib
includedir=\${prefix}/include/spirv_cross
Name: spirv-cross-c-shared
Description: Controlled static SPIRV-Cross C API
Version: $SPIRV_VERSION
Libs: -L\${libdir} -lspirv-cross-c -lspirv-cross-glsl -lspirv-cross-hlsl -lspirv-cross-reflect -lspirv-cross-msl -lspirv-cross-util -lspirv-cross-core -lstdc++ -lpthread
Cflags: -I\${includedir}
EOF
meson_static libplacebo -Ddemos=false -Dtests=false -Dbench=false -Dfuzz=false \
  -Dvulkan=disabled -Dopengl=enabled -Dd3d11=enabled -Dshaderc=enabled \
  -Dglslang=disabled -Dlcms=enabled -Dxxhash=disabled -Dlibdovi=disabled -Ddovi=disabled
if grep -q '^Libs.private:' "$PREFIX/lib/pkgconfig/libplacebo.pc"; then
  sed -i '/^Libs.private:/s/$/ -lstdc++ -lpthread/' "$PREFIX/lib/pkgconfig/libplacebo.pc"
else
  printf '\nLibs.private: -lstdc++ -lpthread\n' >> "$PREFIX/lib/pkgconfig/libplacebo.pc"
fi

mkdir -p builds/ffmpeg
(cd builds/ffmpeg && ../../sources/ffmpeg/configure --prefix="$PREFIX" \
  --pkg-config=pkg-config --pkg-config-flags=--static --cross-prefix=x86_64-w64-mingw32- \
  --arch=x86_64 --target-os=mingw32 --cc="$CC" --cxx="$CXX" --ar="$AR" --ranlib="$RANLIB" --nm="$NM" \
  --disable-autodetect --disable-gpl --disable-nonfree --disable-version3 \
  --enable-static --disable-shared --disable-doc --disable-debug --disable-ffplay --disable-ffprobe \
  --enable-ffmpeg --enable-zlib --enable-libdav1d --enable-ffnvcodec --enable-nvdec \
  --enable-d3d11va --enable-dxva2 --enable-schannel --disable-cuda-llvm \
  --enable-w32threads --disable-pthreads \
  --extra-version=controlled-9d9703e3b6f1 \
  --extra-cflags="$CFLAGS" --extra-cxxflags="$CXXFLAGS" --extra-ldflags="$LDFLAGS" \
  && make -j"$JOBS" && make install)
cp builds/ffmpeg/config.h builds/ffmpeg/config_components.h dist/evidence/
cp builds/ffmpeg/ffbuild/config.mak dist/evidence/ffmpeg-config.mak
for flag in GPL NONFREE VERSION3; do grep -q "^#define CONFIG_$flag 0$" builds/ffmpeg/config.h; done

export MPV_VERSION=v0.41.0-dev-gbaa3e11d4-controlled-lgpl
printf '0.41.0-dev-gbaa3e11d4-controlled-lgpl\n' > sources/mpv/MPV_VERSION
meson setup builds/mpv sources/mpv --cross-file scripts/cross.meson \
  --prefix="$PREFIX" --libdir=lib --buildtype=release --default-library=shared --prefer-static \
  --wrap-mode=nodownload --auto-features=disabled -Dgpl=false -Dlibmpv=true -Dcplayer=false \
  -Dbuild-date=false -Dtests=false -Dlua=luajit \
  -Dgl=enabled -Dgl-win32=enabled -Dplain-gl=enabled -Dgl-dxinterop=enabled \
  -Dgl-dxinterop-d3d9=enabled -Dd3d11=enabled -Ddirect3d=disabled \
  -Dd3d-hwaccel=enabled -Dd3d9-hwaccel=enabled -Dcuda-hwaccel=enabled -Dcuda-interop=enabled \
  -Dwasapi=enabled -Dwin32-threads=enabled -Dvector=enabled \
  -Dshaderc=enabled -Dspirv-cross=enabled -Dlcms2=enabled -Dzimg=enabled -Dzlib=enabled -Diconv=enabled \
  -Dc_link_args="$LDFLAGS -Wl,-Map,/work/dist/evidence/libmpv.map" \
  -Dcpp_link_args="$LDFLAGS -Wl,-Map,/work/dist/evidence/libmpv.map"
grep -q '^#define HAVE_GPL 0$' builds/mpv/config.h
meson compile -C builds/mpv -j "$JOBS"
mkdir -p dist/runtime/include/mpv dist/test-tools
cp builds/mpv/libmpv-2.dll dist/runtime/
cp sources/mpv/include/mpv/*.h dist/runtime/include/mpv/
cp builds/mpv/libmpv.dll.a dist/runtime/ 2>/dev/null || true
cp "$PREFIX/bin/ffmpeg.exe" dist/test-tools/
"$STRIP" dist/runtime/libmpv-2.dll dist/test-tools/ffmpeg.exe
x86_64-w64-mingw32-objdump -p dist/runtime/libmpv-2.dll > dist/evidence/libmpv-pe.txt
cp -r builds/mpv/meson-info dist/evidence/mpv-meson-info
cp builds/mpv/config.h dist/evidence/mpv-config.h
pkg-config --static --libs libass libplacebo > dist/evidence/pkg-config-libs.txt
if grep -Ei '/opt/(ffbuild|upstream-libraries-disabled)|lib(x264|x265|fftw|chromaprint|lcms2_fast_float|lcms2_threaded)' dist/evidence/libmpv.map; then
  echo 'Forbidden inherited/GPL dependency detected in link map'; exit 1
fi
cp README.md REDISTRIBUTION.md sources.lock.json dist/
cp sources/ffmpeg/COPYING.LGPLv3 sources/ffmpeg/COPYING.GPLv3 dist/
cp sources/mpv/Copyright dist/MPV-Copyright.txt
cp -r scripts dist/recipe
python3 scripts/sources.py --collect
(cd dist && find runtime test-tools -type f -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS)
tar --sort=name --mtime="@$SOURCE_DATE_EPOCH" --owner=0 --group=0 --numeric-owner -czf dist/corresponding-sources.tar.gz \
  archives sources.lock.json scripts README.md REDISTRIBUTION.md toolchain-notices upstream-origin.json
