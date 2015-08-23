import ctypes
import numpy as np
import os

nse_c = ctypes.cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'libhydromath.dylib')).nse
nse_c.restype = ctypes.c_double

def nse(obs, sim):
    assert len(obs) == len(sim)

    return nse_c(ctypes.c_void_p(obs.ctypes.data),
                    ctypes.c_void_p(sim.ctypes.data),
                    ctypes.c_int(len(obs)))

