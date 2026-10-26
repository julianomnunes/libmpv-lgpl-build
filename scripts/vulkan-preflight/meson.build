project('controlled-vulkan-preflight', 'c', default_options: ['c_std=c11'])
assert(get_option('prefer_static'), 'Match MPV preference for static libraries')
vulkan = dependency('vulkan', version: '>=1.4.309', required: true)
executable('vulkan-preflight', 'link.c', dependencies: vulkan)
