import ctypes
import numpy as np
import os

rmse_c = ctypes.cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ss_math.so')).rmse
rmse_c.restype = ctypes.c_double

def rmse(obs, sim):
    assert len(obs) == len(sim)

    return rmse_c(ctypes.c_void_p(obs.ctypes.data),
                    ctypes.c_void_p(sim.ctypes.data),
                    ctypes.c_int(len(obs)))

