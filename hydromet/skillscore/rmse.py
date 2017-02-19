import ctypes
from hydromet.hydromath import __lib, __ffi

rmse_c = __lib.rmse

def rmse(obs, sim):
    assert len(obs) == len(sim)

    return rmse_c(__ffi.cast('double *', obs.ctypes.data),
                 __ffi.cast('double *', sim.ctypes.data),
                 len(obs))

