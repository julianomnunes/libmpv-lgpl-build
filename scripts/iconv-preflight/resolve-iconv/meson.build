# Controlled Windows build, 2026-10-26: preserve required static iconv and
# expose its source-built archive directory to Meson's static discovery.
iconv = cc.find_library('iconv',
    dirs: [join_paths(get_option('prefix'), get_option('libdir'))],
    static: true,
    required: get_option('iconv'))
