from gr4j import gr4j

class GR4J(object):
    def __init__(self):
        self.__states = {'production_store': 0, 'routing_store': 0}
        self.__params = {'X1': 0,
                        'X2': 0,
                        'X3': 0,
                        'X4': 0}

    def run(self, p, pe):
        sims, self.__states = gr4j(p, pe, self.__params, self.__states, True)

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
