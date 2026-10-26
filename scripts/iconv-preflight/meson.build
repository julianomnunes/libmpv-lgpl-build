project('controlled-iconv-static-preflight', ['c', 'cpp'],
    meson_version: '>=1.3.0',
    default_options: ['c_std=c11', 'cpp_std=c++20', 'b_lundef=false'])

assert(get_option('prefer_static'), 'Preflight must match MPV prefer_static=true')
assert(get_option('default_library') == 'shared', 'Match MPV default library setting')
assert(get_option('iconv').enabled(), 'iconv must remain explicitly enabled')
cc = meson.get_compiler('c')
cpp = meson.get_compiler('cpp')
subdir('resolve-iconv')
assert(iconv.found(), 'Required static iconv must be found')
assert(cc.has_header('iconv.h'), 'Controlled iconv header must be visible')
assert(cpp.has_header('iconv.h'), 'Controlled iconv header must be visible to C++')
executable('iconv-c', 'link.c', dependencies: iconv)
executable('iconv-cpp', 'link.cpp', dependencies: iconv)
