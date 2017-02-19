import ctypes
from hydromet.hydromath import __lib, __ffi

mse_c = __lib.mse

def mse(obs, sim):
    assert len(obs) == len(sim)

    return mse_c(__ffi.cast('double *', obs.ctypes.data),
                 __ffi.cast('double *', sim.ctypes.data),
                 len(obs))

