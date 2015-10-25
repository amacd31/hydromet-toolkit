import ctypes
from hydromet.hydromath import __lib, __ffi

nse_c = __lib.nse

def nse(obs, sim):
    assert len(obs) == len(sim)

    return nse_c(__ffi.cast('double *', obs.ctypes.data),
                 __ffi.cast('double *', sim.ctypes.data),
                 len(obs))

