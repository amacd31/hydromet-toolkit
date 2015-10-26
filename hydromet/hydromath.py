import os

from ctypes.util import find_library
from cffi import FFI

search_dirs = [
    '/usr/local/include',
    '/usr/include',
]

h_filename = None

for directory in search_dirs:
    tmp_name = os.path.join(directory, 'hydromath.h')
    if os.path.isfile(tmp_name) or os.path.islink(tmp_name):
        h_filename = tmp_name
        break
else:
    print("hydromath.h not found, is it installed?")

if h_filename is not None:
    __ffi = FFI()
    with open(h_filename) as header:
        __ffi.cdef(header.read())

    __lib = __ffi.dlopen('/usr/local/lib/libhydromath.so')
