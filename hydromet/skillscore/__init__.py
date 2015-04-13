from .nse import nse
from .mse import mse
from .rmse import rmse

import ctypes
import numpy as np
import os

ss_math = ctypes.cdll.LoadLibrary(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ss_math.so'))
ss_math.kge.restype = ctypes.c_double

def kge(obs, sim):
    assert len(obs) == len(sim)

    return ss_math.kge(ctypes.c_void_p(obs.ctypes.data),
                    ctypes.c_void_p(sim.ctypes.data),
                    ctypes.c_int(len(obs)))
