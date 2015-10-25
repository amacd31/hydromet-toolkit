import numpy as np

from gr4j import gr4j

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

    def obj_func(self, params, data, qobs, efficiency):
        self.X1 = params[0]
        self.X2 = params[1]
        self.X3 = params[2]
        self.X4 = params[3]

        warmup_data = {
            'P': data['P'][self.warmup_start_date:self.warmup_end_date],
            'PE': data['PE'][self.warmup_start_date:self.warmup_end_date],
        }

        self.warmup(warmup_data)

        calibration_data = {
            'P': data['P'][self.calibration_start_date:self.calibration_end_date],
            'PE': data['PE'][self.calibration_start_date:self.calibration_end_date],
        }

        # Do the simulation!
        sims = np.array(self.run(calibration_data))

        return 1 - efficiency(qobs.ix[self.calibration_start_date:self.calibration_end_date].values, sims)

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
