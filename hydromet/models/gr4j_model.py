import calendar
import numpy as np
from scipy.optimize import differential_evolution

from gr4j import gr4j
from hydromet.skillscore import kge, nse

class GR4J(object):
    def __init__(self):
        self.__states = {'production_store': 0, 'routing_store': 0}
        self.__params = {'X1': 10,
                        'X2': 0,
                        'X3': 10,
                        'X4': 0}

    @property
    def name(self):
        return "gr4j"

    def init(self, warmup_start, warmup_end, calib_start, calib_end):
        self.warmup_start_date = warmup_start
        self.warmup_end_date = warmup_end
        self.calibration_start_date = calib_start
        self.calibration_end_date = calib_end

    def run(self, data, save_states = False):
        sims, states = gr4j(data['P'], data['PE'], self.__params, self.__states, True)

        if save_states:
            self.__states = states

        return sims

    def warmup(self, data):
        # Start with some estimated states
        self.production_store = 0.60 * self.X1
        self.routing_store = 0.70 * self.X3

        # Warm up the model
        return self.run(data)

    def obj_func(self, params, warmup_data, calibration_data, qobs, efficiency):
        self.X1 = params[0]
        self.X2 = params[1]
        self.X3 = params[2]
        self.X4 = params[3]

        self.warmup(warmup_data)

        # Do the simulation!
        sims = np.array(self.run(calibration_data))

        return 1 - efficiency(qobs, sims)

    def calibrate(self, warmup_data, calibration_data, predictand_data):
        bounds = [(10,1500), (-5, 5), (10, 900), (0,5)]

        res_nse = differential_evolution(self.obj_func, bounds, (warmup_data, calibration_data, predictand_data['Q'].values / 148, nse), disp=True)

        self.X1 = res_nse.x[0],
        self.X2 = res_nse.x[1],
        self.X3 = res_nse.x[2],
        self.X4 = res_nse.x[3]

        return res_nse

    def forecast(self, warmup_data, fc_data):

        self.warmup(warmup_data)

        sims = self.run(fc_data)

        return sims

    @property
    def X1(self):
        return self.__params['X1']

    @X1.setter
    def X1(self, value):
        self.__params['X1'] = value

    @property
    def X2(self):
        return self.__params['X2']

    @X2.setter
    def X2(self, value):
        self.__params['X2'] = value

    @property
    def X3(self):
        return self.__params['X3']

    @X3.setter
    def X3(self, value):
        self.__params['X3'] = value

    @property
    def X4(self):
        return self.__params['X4']

    @X4.setter
    def X4(self, value):
        self.__params['X4'] = value

    @property
    def production_store(self):
        return self.__states['production_store']

    @production_store.setter
    def production_store(self, value):
        self.__states['production_store'] = value

    @property
    def routing_store(self):
        return self.__states['routing_store']

    @routing_store.setter
    def routing_store(self, value):
        self.__states['routing_store'] = value
