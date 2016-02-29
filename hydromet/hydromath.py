import os

from ctypes.util import find_library
from cffi import FFI

class MissingLibError(Exception):
    pass

if 'HYDROMATH_DIR' in os.environ:
    HYDROMATH_DIR = os.environ['HYDROMATH_DIR']

    h_filename = os.path.join(HYDROMATH_DIR, 'hydromath.h')
    so_filename = os.path.join(HYDROMATH_DIR, find_library('hydromath'))

    __ffi = FFI()
    with open(h_filename) as header:
        __ffi.cdef(header.read())

    __lib = __ffi.dlopen(so_filename)
else:
    raise MissingLibError("HYDROMATH_DIR environment variable not set. Unable to find libhydromath")
