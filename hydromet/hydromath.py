import os

from ctypes.util import find_library
from cffi import FFI

prefix = find_library('hydromath').split('/lib/')[0]

__ffi = FFI()
with open(os.path.join(prefix, 'include', 'hydromath.h')) as header:
    __ffi.cdef(header.read())

__lib = __ffi.dlopen('hydromath')
